import logging
from utils.tool_wrapper import FunctionTool
from models.comment_request import CommentRequest
from models.comment_response import CommentResponse
from services.comment_assistant_service import CommentAssistantService

logger = logging.getLogger(__name__)
_comment_service = CommentAssistantService()


def reply_to_comment(request: CommentRequest) -> CommentResponse:
    """
    Analyzes an incoming public social media comment and generates brand-consistent reply variations.
    Provide a CommentRequest containing the original post, incoming comment, platform, and brand profile.
    """
    logger.info(f"Executing 'reply_to_comment' for platform '{request.platform}'.")

    try:
        if not request.incoming_comment or not request.incoming_comment.strip():
            raise ValueError("Validation Error: The incoming comment text cannot be empty.")

        if not request.original_post or not request.original_post.strip():
            raise ValueError("Validation Error: The original post context must be provided.")

        response = _comment_service.generate_reply(request)
        logger.info(f"Comment analysis complete. Sentiment: {response.detected_sentiment.value}. Human Escalation: {response.requires_human_attention}.")
        return response

    except ValueError as ve:
        logger.warning(f"Bad Request in reply_to_comment: {ve}")
        raise
    except Exception as e:
        logger.error(f"Unexpected execution error in reply_to_comment: {e}", exc_info=True)
        raise RuntimeError(f"Tool Execution Failed: Unable to analyze comment -> {str(e)}")


comment_tool = FunctionTool(func=reply_to_comment)
