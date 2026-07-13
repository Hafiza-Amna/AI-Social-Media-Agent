"""
app.py — FastAPI Application Entry Point
AI Social Media Agent | Google ADK 2.3.0 + Gemini 2.5 Flash Lite
"""
import logging
import uuid
from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()  # Load GEMINI_API_KEY and all other env vars from .env before anything else initializes

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from router import AIIntentRouter

# ─────────────────────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Request / Response Schemas
# ─────────────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    """Payload accepted by the POST /chat endpoint."""
    message: str = Field(..., min_length=1, description="The user's natural language message.")
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Optional user ID for session tracking.")

class ChatResponse(BaseModel):
    """Structured response returned by the POST /chat endpoint."""
    user_id: str
    message: str
    response: str
    status: str = "success"

# ─────────────────────────────────────────────────────────────────────────────
# Application Lifespan — initializes singletons on startup
# ─────────────────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup/shutdown lifecycle manager.
    Initializes the AIIntentRouter (and the underlying ADK Runner + InMemorySessionService)
    once at startup and stores it in app.state for use across all requests.
    """
    logger.info("Starting AI Social Media Agent API...")
    app.state.router = AIIntentRouter()
    logger.info("Master Agent, Runner, and SessionService initialized successfully.")
    yield
    logger.info("Shutting down AI Social Media Agent API.")

# ─────────────────────────────────────────────────────────────────────────────
# FastAPI App
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="AI Social Media Agent API",
    description=(
        "Production-ready AI Social Media Management API powered by Google ADK 2.3.0 "
        "and Gemini 2.5 Flash Lite. Supports content generation, scheduling, publishing, "
        "analytics, competitor analysis, and more."
    ),
    version="1.0.0",
    lifespan=lifespan
)

# ─────────────────────────────────────────────────────────────────────────────
# CORS Middleware — allows the frontend to call this API
# ─────────────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Restrict to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────────────────────
# Global Exception Handler
# ─────────────────────────────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception at {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"status": "error", "detail": "An internal server error occurred. Please try again."}
    )

# ─────────────────────────────────────────────────────────────────────────────
# Health Check
# ─────────────────────────────────────────────────────────────────────────────
from config import settings

@app.get("/health", tags=["System"])
async def health_check():
    """Lightweight health check endpoint for load balancers and monitoring tools."""
    return {"status": "healthy", "agent": "social_media_master_agent", "model": settings.MODEL_NAME}

# ─────────────────────────────────────────────────────────────────────────────
# Core Chat Endpoint
# ─────────────────────────────────────────────────────────────────────────────
@app.post("/chat", response_model=ChatResponse, tags=["Agent"])
async def chat(request: ChatRequest, fastapi_request: Request):
    """
    Primary conversational endpoint.
    
    Accepts a user message and passes it through the Google ADK 2.3.0 Runner.
    The Master Agent (Gemini 2.5 Flash Lite) autonomously selects and executes the
    correct tool based on the user's intent, then returns a synthesized response.
    """
    logger.info(f"POST /chat | user_id='{request.user_id}' | message='{request.message}'")

    router: AIIntentRouter = fastapi_request.app.state.router

    # Validate message is not just whitespace (Pydantic min_length handles empty strings)
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be blank or whitespace-only.")

    # Route through the ADK agent asynchronously
    agent_response = await router.process_request_async(
        user_message=request.message,
        user_id=request.user_id
    )

    return ChatResponse(
        user_id=request.user_id,
        message=request.message,
        response=agent_response
    )

# ─────────────────────────────────────────────────────────────────────────────
# Application Entry Point
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
@app.get("/")
def home():
    return {
        "message": "AI Social Media Agent is running"
    }