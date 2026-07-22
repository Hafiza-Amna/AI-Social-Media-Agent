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
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

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

from typing import Optional

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
    job_id: Optional[str] = None
    pending_review: bool = False
    platform: Optional[str] = None

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
    # Ensure publish_jobs table exists before any request is handled
    from database import init_db
    init_db()
    logger.info("Database tables verified/created.")
    app.state.router = AIIntentRouter()
    logger.info("Master Agent, Runner, and SessionService initialized successfully.")
    yield
    logger.info("Shutting down AI Social Media Agent API.")

# ─────────────────────────────────────────────────────────────────────────────
# Rate Limiter — IP-based, 20 requests per minute on /chat
# ─────────────────────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)

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

# Attach the rate limiter state and 429 handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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
# Mount Frontend Static Assets
# ─────────────────────────────────────────────────────────────────────────────
frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

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
@limiter.limit("20/minute")
async def chat(request: Request, body: ChatRequest):
    """
    Primary conversational endpoint.
    
    Accepts a user message and passes it through the Google ADK 2.3.0 Runner.
    The Master Agent (Gemini 2.5 Flash Lite) autonomously selects and executes the
    correct tool based on the user's intent, then returns a synthesized response.
    """
    logger.info(f"POST /chat | user_id='{body.user_id}' | message='{body.message}'")

    router: AIIntentRouter = request.app.state.router

    # Validate message is not just whitespace (Pydantic min_length handles empty strings)
    if not body.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be blank or whitespace-only.")

    # Route through the ADK agent asynchronously
    agent_response = await router.process_request_async(
        user_message=body.message,
        user_id=body.user_id
    )

    # The router returns a JSON string when a publish tool runs (contains job_id)
    import json as _json
    job_id: Optional[str] = None
    pending_review: bool = False
    platform_out: Optional[str] = None
    response_text: str

    if isinstance(agent_response, str):
        try:
            parsed = _json.loads(agent_response)
            if isinstance(parsed, dict) and "job_id" in parsed:
                job_id = parsed.get("job_id")
                response_text = parsed.get("response", agent_response)
                pending_review = parsed.get("status") == "pending_review"
                platform_out = parsed.get("platform")
            else:
                response_text = agent_response
        except (_json.JSONDecodeError, TypeError):
            response_text = agent_response
    else:
        response_text = str(agent_response)

    return ChatResponse(
        user_id=body.user_id,
        message=body.message,
        response=response_text,
        job_id=job_id,
        pending_review=pending_review,
        platform=platform_out,
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
# Publishing Management Endpoints
# ─────────────────────────────────────────────────────────────────────────────
from datetime import datetime
from models.publish_job import PublishJob, PublishStatus
from database import SessionLocal
from services.auto_publishing_service import AutoPublishingService

_auto_service = AutoPublishingService()


@app.get("/jobs", tags=["Publishing"])
def list_jobs(status: Optional[str] = None):
    """
    List all publishing jobs in the queue.
    Optionally filter by status: pending_review, approved, rejected, published, failed.
    """
    db = SessionLocal()
    try:
        query = db.query(PublishJob)
        if status:
            query = query.filter(PublishJob.status == status)
        jobs = query.order_by(PublishJob.scheduled_datetime.desc()).all()
        return {"jobs": [j.to_dict() for j in jobs], "total": len(jobs)}
    finally:
        db.close()


@app.post("/execute_job/{job_id}", tags=["Publishing"])
def execute_job(job_id: str):
    """
    Manually trigger the publishing of an approved job.
    The job must have status='approved' for this to succeed.
    """
    result = _auto_service.execute_job(job_id)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    return {
        "success": True, 
        "message": result.message, 
        "job": result.job,
        "publication_id": result.publication_id,
        "publication_url": getattr(result, "publication_url", None)
    }

class ReviewRequest(BaseModel):
    action: str = Field(..., description="The action to perform: 'approve', 'reject', or 'edit'.")
    content: Optional[str] = Field(None, description="The updated content if action is 'edit'.")
    reviewer: Optional[str] = Field("Human Reviewer", description="The identity of the reviewer.")

@app.post("/review/{job_id}", tags=["Review"])
def review_job(job_id: str, body: ReviewRequest):
    """
    Review a pending publishing job.
    Supported actions: approve, reject, edit.
    """
    db = SessionLocal()
    try:
        job = db.query(PublishJob).filter(PublishJob.job_id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job ID not found in the database.")

        # Validation: already published posts cannot be reviewed again
        if job.status in [PublishStatus.PUBLISHED.value, "Published", "published"]:
            raise HTTPException(
                status_code=400,
                detail="Validation Error: Already published posts cannot be reviewed again."
            )

        action_lower = body.action.lower().strip()
        if action_lower not in ["approve", "reject", "edit"]:
            raise HTTPException(
                status_code=400,
                detail=f"Validation Error: Invalid review action '{body.action}'. Supported actions: approve, reject, edit."
            )

        if action_lower == "edit":
            if not body.content or not body.content.strip():
                raise HTTPException(
                    status_code=400,
                    detail="Validation Error: Content cannot be empty for 'edit' action."
                )
            job.content = body.content
            job.status = PublishStatus.APPROVED.value
        elif action_lower == "approve":
            job.status = PublishStatus.APPROVED.value
        elif action_lower == "reject":
            job.status = PublishStatus.REJECTED.value

        # Store review metadata
        job.reviewer = body.reviewer
        job.reviewed_at = datetime.utcnow()
        job.review_action = action_lower

        db.commit()
        db.refresh(job)
        saved_job = job.to_dict()

        # Auto-publish immediately when approved or edited+approved
        if action_lower in ("approve", "edit"):
            publish_result = _auto_service.execute_job(job_id)
            return {
                "success": publish_result.success,
                "message": publish_result.message,
                "review_action": action_lower,
                "job": publish_result.job or saved_job,
                "publication_id": publish_result.publication_id,
                "publication_url": getattr(publish_result, "publication_url", None)
            }

        return {
            "success": True,
            "message": f"Job successfully updated with action '{action_lower}'.",
            "job": saved_job,
        }
    finally:
        db.close()

# ─────────────────────────────────────────────────────────────────────────────
# Application Entry Point
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/", tags=["Dashboard"])
@app.get("/dashboard", tags=["Dashboard"])
def home():
    index_file = os.path.join(os.path.dirname(__file__), "frontend", "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {
        "message": "AI Social Media Agent is running"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)