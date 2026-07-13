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


def publish_to_linkedin_tool(content: str) -> dict:
    """
    Publishes the generated content immediately to the user's real LinkedIn profile.
    Provide the exact text content to publish.
    """
    from services.linkedin_service import publish_to_linkedin
    return publish_to_linkedin(content)


linkedin_publish_tool = FunctionTool(func=publish_to_linkedin_tool)

