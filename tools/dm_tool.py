import logging
from utils.tool_wrapper import FunctionTool
from models.dm_request import DMRequest
from models.dm_response import DMResponse
from services.dm_assistant_service import DMAssistantService

logger = logging.getLogger(__name__)
_dm_service = DMAssistantService()


def reply_to_dm(request: DMRequest) -> DMResponse:
    """
    Analyzes an incoming direct message (DM), determines user intent, and generates context-aware replies.
    Provide a DMRequest containing the incoming message, conversation history, platform, and brand profile.
    """
    logger.info(f"Executing 'reply_to_dm' for platform '{request.platform}'.")

    try:
        if not request.incoming_message or not request.incoming_message.strip():
            raise ValueError("Validation Error: The incoming direct message text cannot be empty.")

        response = _dm_service.generate_reply(request)
        intent_val = getattr(response.detected_intent, 'value', response.detected_intent)
        logger.info(f"DM analysis complete. Intent: {intent_val}. Escalation Required: {response.requires_escalation}.")
        return response

    except ValueError as ve:
        logger.warning(f"Bad Request in reply_to_dm: {ve}")
        raise
    except Exception as e:
        logger.error(f"Unexpected execution error in reply_to_dm: {e}", exc_info=True)
        raise RuntimeError(f"Tool Execution Failed: Unable to analyze direct message -> {str(e)}")


dm_tool = FunctionTool(func=reply_to_dm)
