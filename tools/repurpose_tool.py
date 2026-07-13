import logging
from utils.tool_wrapper import FunctionTool
from models.repurpose_request import RepurposeRequest
from models.repurpose_response import RepurposeResponse
from services.content_repurposing_service import ContentRepurposingService

logger = logging.getLogger(__name__)
_repurpose_service = ContentRepurposingService()


def repurpose_content(request: RepurposeRequest) -> RepurposeResponse:
    """
    Transforms a single piece of content into highly optimized, platform-native posts across multiple social networks.
    Provide a RepurposeRequest with the original content, source platform, target platforms, tone, and audience.
    """
    logger.info(f"Executing 'repurpose_content'. Source: '{request.source_platform.value}'. Targets: {len(request.target_platforms)}")

    try:
        if not request.original_content or not request.original_content.strip():
            raise ValueError("Validation Error: The original content cannot be empty.")

        if not request.target_platforms or len(request.target_platforms) == 0:
            raise ValueError("Validation Error: At least one target platform must be specified.")

        response = _repurpose_service.repurpose_content(request)
        logger.info(f"Content repurposed into {len(response.repurposed_posts)} formats. Quality Score: {response.quality_score}/100.")
        return response

    except ValueError as ve:
        logger.warning(f"Bad Request in repurpose_content: {ve}")
        raise
    except Exception as e:
        logger.error(f"Unexpected execution error in repurpose_content: {e}", exc_info=True)
        raise RuntimeError(f"Tool Execution Failed: Unable to repurpose content -> {str(e)}")


repurpose_tool = FunctionTool(func=repurpose_content)
