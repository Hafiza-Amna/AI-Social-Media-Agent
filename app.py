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
# LinkedIn OAuth Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/linkedin/login", tags=["LinkedIn OAuth"])
def linkedin_login(request: Request):
    """
    Redirects the user to LinkedIn's OAuth authorization page.
    """
    from fastapi.responses import RedirectResponse
    import urllib.parse

    client_id = settings.LINKEDIN_CLIENT_ID
    if not client_id:
        raise HTTPException(
            status_code=400,
            detail="LINKEDIN_CLIENT_ID is not configured in settings/environment."
        )

    # In a real production app, use a dynamically generated random state.
    state = "linkedin_agent_oauth_state"
    # Construct redirect URI dynamically from request base URL
    base_url = str(request.base_url).rstrip("/")
    redirect_uri = f"{base_url}/linkedin/callback"
    scopes = "openid profile email w_member_social"

    auth_url = (
        "https://www.linkedin.com/oauth/v2/authorization?"
        f"response_type=code&"
        f"client_id={client_id}&"
        f"redirect_uri={urllib.parse.quote(redirect_uri)}&"
        f"state={state}&"
        f"scope={urllib.parse.quote(scopes)}"
    )
    
    return RedirectResponse(auth_url)


@app.get("/linkedin/callback", tags=["LinkedIn OAuth"])
def linkedin_callback(request: Request, code: str = None, state: str = None, error: str = None, error_description: str = None):
    """
    Processes the OAuth callback, exchanges authorization code for access token,
    and updates config & .env file.
    """
    from fastapi.responses import HTMLResponse
    import requests

    if error:
        return HTMLResponse(
            content=f"<h3>Authentication Failed</h3><p>{error}: {error_description}</p>",
            status_code=400
        )

    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code.")

    client_id = settings.LINKEDIN_CLIENT_ID
    client_secret = settings.LINKEDIN_CLIENT_SECRET
    
    # Construct redirect URI dynamically from request base URL
    base_url = str(request.base_url).rstrip("/")
    redirect_uri = f"{base_url}/linkedin/callback"

    if not client_id or not client_secret:
        raise HTTPException(
            status_code=500,
            detail="LinkedIn configuration is incomplete. Missing client_id or client_secret."
        )

    # Exchange authorization code for Access Token
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret,
    }

    try:
        response = requests.post(token_url, data=payload)
        if response.status_code != 200:
            return HTMLResponse(
                content=f"<h3>Token Exchange Failed</h3><p>Status: {response.status_code}</p><pre>{response.text}</pre>",
                status_code=400
            )

        token_data = response.json()
        access_token = token_data.get("access_token")
        if not access_token:
            return HTMLResponse(
                content="<h3>Token Exchange Failed</h3><p>Access token was not found in response payload.</p>",
                status_code=400
            )

        # Securely store access token
        from services.linkedin_service import LinkedInService
        LinkedInService.update_env_token(access_token)

        success_html = """
        <html>
        <head>
            <title>Authentication Successful</title>
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; background-color: #f3f6f8; margin: 0; }
                .card { background: white; padding: 40px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); text-align: center; max-width: 450px; }
                h1 { color: #0a66c2; font-size: 24px; margin-bottom: 16px; }
                p { color: #5e5e5e; font-size: 16px; line-height: 1.5; margin-bottom: 24px; }
                .success-badge { color: #057642; background-color: #e1f4e9; font-weight: 600; padding: 6px 12px; border-radius: 4px; display: inline-block; margin-bottom: 20px; }
            </style>
        </head>
        <body>
            <div class="card">
                <div class="success-badge">✓ Authorization Successful</div>
                <h1>LinkedIn Connected!</h1>
                <p>The AI Social Media Agent has securely stored your Access Token and is now ready to post to your LinkedIn profile.</p>
                <p style="font-size: 14px; color: #8c8c8c;">You can now close this tab and start publishing.</p>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=success_html)

    except Exception as e:
        logger.error(f"Error during token exchange callback: {e}", exc_info=True)
        return HTMLResponse(
            content=f"<h3>Internal Server Error</h3><p>{str(e)}</p>",
            status_code=500
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