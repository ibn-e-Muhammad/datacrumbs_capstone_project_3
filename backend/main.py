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

# --- Monkey Patch for langchain-google-genai bug ---
import langchain_google_genai.chat_models

PATCH_CODE = """
def _patched_response_to_result(response, stream=False, prev_usage=None):
    llm_output = {"prompt_feedback": proto.Message.to_dict(response.prompt_feedback)}

    prev_input_tokens = prev_usage["input_tokens"] if prev_usage else 0
    prev_output_tokens = prev_usage["output_tokens"] if prev_usage else 0
    prev_total_tokens = prev_usage["total_tokens"] if prev_usage else 0

    try:
        input_tokens = response.usage_metadata.prompt_token_count
        output_tokens = response.usage_metadata.candidates_token_count
        total_tokens = response.usage_metadata.total_token_count
        cache_read_tokens = response.usage_metadata.cached_content_token_count
        if input_tokens + output_tokens + cache_read_tokens + total_tokens > 0:
            lc_usage = UsageMetadata(
                input_tokens=input_tokens - prev_input_tokens,
                output_tokens=output_tokens - prev_output_tokens,
                total_tokens=total_tokens - prev_total_tokens,
                input_token_details={"cache_read": cache_read_tokens},
            )
        else:
            lc_usage = None
    except AttributeError:
        lc_usage = None

    generations = []

    for candidate in response.candidates:
        generation_info = {}
        if candidate.finish_reason:
            # FIX: Safe extraction for integer finish reasons
            if hasattr(candidate.finish_reason, "name"):
                generation_info["finish_reason"] = candidate.finish_reason.name
            else:
                generation_info["finish_reason"] = str(candidate.finish_reason)
                
        generation_info["safety_ratings"] = [
            proto.Message.to_dict(safety_rating, use_integers_for_enums=False)
            for safety_rating in candidate.safety_ratings
        ]
        message = _parse_response_candidate(candidate, streaming=stream)
        message.usage_metadata = lc_usage
        if stream:
            generations.append(
                ChatGenerationChunk(
                    message=cast(AIMessageChunk, message),
                    generation_info=generation_info,
                )
            )
        else:
            generations.append(
                ChatGeneration(message=message, generation_info=generation_info)
            )
    if not response.candidates:
        logger.warning(
            "Gemini produced an empty response. Continuing with empty message\\n"
            f"Feedback: {response.prompt_feedback}"
        )
        if stream:
            generations = [
                ChatGenerationChunk(
                    message=AIMessageChunk(content=""), generation_info={}
                )
            ]
        else:
            generations = [ChatGeneration(message=AIMessage(""), generation_info={})]
    return ChatResult(generations=generations, llm_output=llm_output)
"""
exec(PATCH_CODE, langchain_google_genai.chat_models.__dict__)
langchain_google_genai.chat_models._response_to_result = langchain_google_genai.chat_models._patched_response_to_result
# ---------------------------------------------------

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
