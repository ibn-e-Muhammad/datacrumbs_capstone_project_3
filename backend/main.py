"""
FastAPI entry point for the ACME Corporation AI Agent backend.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from models.schemas import ChatRequest, ChatResponse, HealthResponse
from services.rag_service import initialize_vector_store
from services.agent_service import chat

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the FastAPI application."""
    logger.info("Starting up backend service...")
    try:
        # Initialize the vector store from local documents
        initialize_vector_store()
        logger.info("FAISS index initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize FAISS index: {e}")
        # We don't raise here so the server still starts, but RAG won't work.
    
    yield
    
    logger.info("Shutting down backend service...")

# Initialize FastAPI app
app = FastAPI(
    title="ACME Corporation Customer Support API",
    description="Backend for the AI-powered customer support agent.",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="ok")

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Process a chat message using the AI agent.
    """
    try:
        logger.info(f"Received chat request: {request.message[:50]}...")
        result = await chat(request.message, request.conversation_id)
        return ChatResponse(
            reply=result["reply"],
            conversation_id=result["conversation_id"]
        )
    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
