"""
tools/publishing_tool.py

Tool wrapper for the auto-publishing workflow.
"""
import logging
from datetime import datetime
from utils.tool_wrapper import FunctionTool
from models.publish_request import PublishRequest
from models.publish_response import PublishResponse
from services.auto_publish_service import AutoPublishService

logger = logging.getLogger(__name__)
_publish_service = AutoPublishService()


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
    Publishes the generated content immediately to the authenticated user's real LinkedIn profile
    using the stored LINKEDIN_ACCESS_TOKEN. Call this tool after generating post content whenever
    the user asks to post, publish, or share content on LinkedIn.
    Expects a 'content' field with the exact text to publish.
    Returns a JSON object with 'success' (bool), 'publication_id' (str), and 'message' (str).
    """
    logger.info("[linkedin_publish_tool] Invoked — preparing to publish to LinkedIn API.")
    from services.linkedin_service import publish_to_linkedin
    result = publish_to_linkedin(request.content)
    if result.get("success"):
        logger.info(f"[linkedin_publish_tool] SUCCESS — publication_id: {result.get('publication_id')}")
    else:
        logger.error(f"[linkedin_publish_tool] FAILED — {result.get('message')}")
    return result


linkedin_publish_tool = FunctionTool(func=publish_to_linkedin_tool)
