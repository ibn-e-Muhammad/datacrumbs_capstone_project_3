"""
RAG (Retrieval-Augmented Generation) service.

Responsibilities
-----------------
1. Load company documents (``Company_sample.txt``, ``Company_products.xlsx``)
2. Split them into chunks using ``RecursiveCharacterTextSplitter``
3. Embed chunks with ``GoogleGenerativeAIEmbeddings`` (text-embedding-002)
4. Persist / load a FAISS vector store to/from disk
5. Expose a ``retriever`` for similarity search (k=3)

The retriever is consumed by the agent tools layer — this module has no
direct dependency on the agent or the web framework.
"""

import logging
from pathlib import Path
from typing import List

from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import UnstructuredExcelLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import (
    COMPANY_TXT_PATH,
    COMPANY_XLSX_PATH,
    FAISS_INDEX_DIR,
    get_settings,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------
_vector_store: FAISS | None = None


# ---------------------------------------------------------------------------
# Document loading helpers
# ---------------------------------------------------------------------------

def _load_documents() -> List[Document]:
    """Load all company data files into LangChain ``Document`` objects.

    Returns:
        A flat list of documents from all available sources.

    Raises:
        FileNotFoundError: If the primary text file is missing.
    """
    documents: List[Document] = []

    # --- Company overview (plain text) ---
    txt_path = Path(COMPANY_TXT_PATH)
    if txt_path.exists():
        logger.info("Loading text document: %s", txt_path)
        loader = TextLoader(str(txt_path), encoding="utf-8")
        documents.extend(loader.load())
    else:
        logger.warning("Company text file not found at %s", txt_path)

    # --- Product catalogue (Excel) ---
    xlsx_path = Path(COMPANY_XLSX_PATH)
    if xlsx_path.exists():
        logger.info("Loading Excel document: %s", xlsx_path)
        try:
            loader = UnstructuredExcelLoader(str(xlsx_path), mode="elements")
            documents.extend(loader.load())
        except Exception:
            logger.exception(
                "Failed to load Excel file at %s. "
                "Continuing with text data only.",
                xlsx_path,
            )
    else:
        logger.warning(
            "Company products file not found at %s. "
            "RAG will use text data only.",
            xlsx_path,
        )

    if not documents:
        raise FileNotFoundError(
            "No company data files found. Ensure at least "
            f"'{COMPANY_TXT_PATH}' exists at the project root."
        )

    logger.info("Loaded %d raw document(s) from disk.", len(documents))
    return documents


def _split_documents(documents: List[Document]) -> List[Document]:
    """Chunk documents using ``RecursiveCharacterTextSplitter``.

    Uses ``chunk_size=500`` and ``chunk_overlap=50`` as prescribed by
    the RAG-engineer skill guidelines.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = splitter.split_documents(documents)
    logger.info("Split documents into %d chunks.", len(chunks))
    return chunks


# ---------------------------------------------------------------------------
# Embedding model
# ---------------------------------------------------------------------------

def _get_embeddings() -> GoogleGenerativeAIEmbeddings:
    """Instantiate the Google Generative AI embedding model."""
    settings = get_settings()
    return GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=settings.google_api_key,
    )


# ---------------------------------------------------------------------------
# Vector store management
# ---------------------------------------------------------------------------

def _build_vector_store() -> FAISS:
    """Build a FAISS index from scratch and persist it to disk."""
    documents = _load_documents()
    chunks = _split_documents(documents)
    embeddings = _get_embeddings()

    logger.info("Building FAISS index from %d chunks …", len(chunks))
    store = FAISS.from_documents(chunks, embeddings)

    # Ensure the target directory exists
    FAISS_INDEX_DIR.mkdir(parents=True, exist_ok=True)
    store.save_local(str(FAISS_INDEX_DIR))
    logger.info("FAISS index persisted to %s", FAISS_INDEX_DIR)

    return store


def _load_vector_store() -> FAISS:
    """Load a previously persisted FAISS index from disk."""
    embeddings = _get_embeddings()
    logger.info("Loading FAISS index from %s …", FAISS_INDEX_DIR)
    store = FAISS.load_local(
        str(FAISS_INDEX_DIR),
        embeddings,
        allow_dangerous_deserialization=True,
    )
    return store


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def initialize_vector_store(force_rebuild: bool = False) -> FAISS:
    """Initialise (or re-build) the FAISS vector store.

    The store is built from raw documents when:
    * No persisted index exists on disk, **or**
    * ``force_rebuild`` is ``True``.

    Otherwise the existing index is loaded from disk for fast startup.

    Args:
        force_rebuild: If ``True``, always re-index from source documents.

    Returns:
        The ready-to-query ``FAISS`` vector store instance.
    """
    global _vector_store

    index_file = FAISS_INDEX_DIR / "index.faiss"

    if force_rebuild or not index_file.exists():
        logger.info("Building vector store (force_rebuild=%s) …", force_rebuild)
        _vector_store = _build_vector_store()
    else:
        logger.info("Loading existing vector store from disk …")
        _vector_store = _load_vector_store()

    return _vector_store


def get_retriever():
    """Return a LangChain retriever backed by the FAISS vector store.

    Uses similarity search with ``k=3`` to return the top-3 most
    relevant chunks for any given query.

    Raises:
        RuntimeError: If the vector store has not been initialised yet.
    """
    if _vector_store is None:
        raise RuntimeError(
            "Vector store is not initialised. "
            "Call initialize_vector_store() during app startup."
        )
    return _vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3},
    )


def search_knowledge(query: str) -> str:
    """Run a similarity search and return formatted context.

    This is the function that the agent tool wraps.

    Args:
        query: The natural-language question to search for.

    Returns:
        A formatted string of the top-3 matching document chunks,
        or a "no results" message.
    """
    retriever = get_retriever()
    docs = retriever.invoke(query)

    if not docs:
        return "No relevant information found in the company knowledge base."

    results: list[str] = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "unknown")
        results.append(
            f"--- Result {i} (source: {source}) ---\n{doc.page_content}"
        )

    return "\n\n".join(results)
