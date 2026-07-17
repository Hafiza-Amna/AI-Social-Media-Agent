"""
tools/publishing_tool.py

Tool wrapper for the auto-publishing workflow.
"""
import logging
from datetime import datetime
from utils.tool_wrapper import FunctionTool
from models.publish_request import PublishRequest
from models.publish_response import PublishResponse
from services.auto_publishing_service import AutoPublishingService

logger = logging.getLogger(__name__)
_publish_service = AutoPublishingService()


def publish_post(request: PublishRequest) -> PublishResponse:
    """
    Executes or schedules the publishing of content to a social media platform.
    Provide a PublishRequest containing the platform, scheduled time, and text content.
    """
    logger.info(f"Executing 'publish_post' for platform '{request.platform}'. Scheduled for: {request.scheduled_datetime}")

    try:
        if not request.content or not request.content.strip():
            raise ValueError("Validation Error: The post content cannot be empty.")

        # Parse datetime string for validation (service handles it internally too)
        try:
            scheduled_dt = datetime.fromisoformat(request.scheduled_datetime)
            if scheduled_dt.replace(tzinfo=None) < datetime.utcnow():
                logger.warning(f"Scheduled time ({request.scheduled_datetime}) is in the past. Defaulting to immediate publish.")
        except (ValueError, TypeError):
            logger.warning(f"Could not parse scheduled_datetime '{request.scheduled_datetime}'.")

        response = _publish_service.publish_post(request)
        logger.info(f"Publishing workflow completed for '{request.platform}'. Status: {response.publishing_status}.")
        return response

    except ValueError as ve:
        logger.warning(f"Bad Request in publish_post: {ve}")
        raise
    except Exception as e:
        logger.error(f"Unexpected execution error in publish_post: {e}", exc_info=True)
        raise RuntimeError(f"Tool Execution Failed: Unable to execute publishing workflow -> {str(e)}")


publishing_tool = FunctionTool(func=publish_post)


# ---------------------------------------------------------------------------
# LinkedIn Real Publishing Tool
# ---------------------------------------------------------------------------
from pydantic import BaseModel, Field


class LinkedInPublishRequest(BaseModel):
    content: str = Field(
        ...,
        description="The full text content to publish as a LinkedIn post on the authenticated user's profile.",
    )


def publish_to_linkedin_tool(request: LinkedInPublishRequest) -> dict:
    """
    Saves the generated content to the database with pending_review status for human approval.
    Does NOT publish immediately.
    """
    logger.info("[linkedin_publish_tool] Invoked — queuing for approval in SQLite.")
    response = _publish_service.publish_post(PublishRequest(
        platform="LinkedIn",
        content=request.content,
        scheduled_datetime=datetime.utcnow().isoformat()
    ))
    return {
        "success": response.success,
        "job_id": response.job["job_id"] if response.job else None,
        "content": request.content,
        "message": response.message
    }


linkedin_publish_tool = FunctionTool(func=publish_to_linkedin_tool)


# ---------------------------------------------------------------------------
# Instagram Real Publishing Tool
# ---------------------------------------------------------------------------

class InstagramPublishRequest(BaseModel):
    content: str = Field(
        ...,
        description="The text caption content for the Instagram post.",
    )
    media_url: str = Field(
        ...,
        description="The public URL of the image or video to publish to Instagram. Instagram requires media to be published.",
    )


def publish_to_instagram_tool(content: str = None, media_url: str = None, request: InstagramPublishRequest = None) -> dict:
    """
    Saves content to the database with pending_review status for human approval.
    Does NOT publish immediately.
    """
    logger.info("[instagram_publish_tool] Invoked — queuing for approval in SQLite.")
    
    # Gracefully handle if the first positional arg is actually the Pydantic request object
    if isinstance(content, InstagramPublishRequest):
        request = content
        content = request.content
        media_url = request.media_url
    elif request is not None:
        content = request.content
        media_url = request.media_url

    # Construct the Pydantic request model to ensure validation
    req_obj = InstagramPublishRequest(content=content, media_url=media_url)

    response = _publish_service.publish_post(PublishRequest(
        platform="Instagram",
        content=req_obj.content,
        media_urls=[req_obj.media_url],
        scheduled_datetime=datetime.utcnow().isoformat()
    ))
    return {
        "success": response.success,
        "job_id": response.job["job_id"] if response.job else None,
        "content": req_obj.content,
        "media_url": req_obj.media_url,
        "message": response.message
    }


instagram_publish_tool = FunctionTool(func=publish_to_instagram_tool)


