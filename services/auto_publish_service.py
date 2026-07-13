"""
services/auto_publish_service.py

Handles execution of scheduled social media posts.
Platform is now a plain str, datetime is parsed from ISO string.
"""
import uuid
import logging
from datetime import datetime
from models.publish_request import PublishRequest
from models.publish_response import PublishResponse

logger = logging.getLogger(__name__)


class AutoPublishService:
    """
    Service responsible for handling the execution of scheduled social media posts.
    It validates incoming requests and simulates the publishing workflow.
    Real API integrations (Facebook, Instagram, LinkedIn, X) will be injected here later.
    """

    def publish_post(self, request: PublishRequest) -> PublishResponse:
        """
        Validates the publishing request and simulates the API posting process.
        Returns a structured PublishResponse detailing the outcome.
        """
        # Parse the ISO datetime string
        try:
            scheduled_dt = datetime.fromisoformat(request.scheduled_datetime)
        except (ValueError, TypeError):
            scheduled_dt = datetime.utcnow()
            logger.warning(f"Could not parse scheduled_datetime '{request.scheduled_datetime}', defaulting to now.")

        # 1. Validation Phase
        if not request.content or request.content.strip() == "":
            return PublishResponse(
                publishing_status="Failed",
                platform=request.platform,
                scheduled_time=scheduled_dt,
                message="Validation Error: Post content cannot be empty.",
                publication_id=None
            )

        if scheduled_dt < datetime.utcnow():
            logger.warning("Scheduled time is in the past. Executing immediately as a catch-up post.")

        # 2. Simulation Phase
        logger.info(f"Simulating publishing to {request.platform}...")
        logger.debug(f"Content: {request.content}")
        if request.media_urls:
            logger.debug(f"Media attached: {len(request.media_urls)} items.")

        # TODO: Integrate actual platform APIs (Facebook, Instagram, LinkedIn, X) here

        # Generate a simulated publication ID
        platform_slug = request.platform.lower().replace(" ", "_").replace("(", "").replace(")", "")
        simulated_pub_id = f"{platform_slug}_post_{uuid.uuid4().hex[:8]}"

        # 3. Return Success Response
        return PublishResponse(
            publishing_status="Success (Simulated)",
            platform=request.platform,
            scheduled_time=scheduled_dt,
            message=f"Successfully simulated publishing to {request.platform}.",
            publication_id=simulated_pub_id
        )
