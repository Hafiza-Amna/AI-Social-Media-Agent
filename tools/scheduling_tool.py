import logging
from utils.tool_wrapper import FunctionTool
from models.schedule_request import ScheduleRequest
from models.schedule_response import ScheduleResponse
from services.smart_schedule_service import SmartScheduleService

logger = logging.getLogger(__name__)
_schedule_service = SmartScheduleService()


def analyze_schedule(request: ScheduleRequest) -> ScheduleResponse:
    """
    Analyzes historical audience activity and recommends the absolute best posting times.
    Provide a ScheduleRequest including the platform, timezone, content type, and raw audience data.
    """
    logger.info(f"Executing 'analyze_schedule' for platform '{request.platform}'. Content Type: '{request.content_type}'")

    try:
        if not request.audience_activity_data or not request.audience_activity_data.strip():
            raise ValueError("Validation Error: Audience activity data must be provided for accurate analysis.")

        if request.posting_frequency <= 0:
            raise ValueError("Validation Error: Target posting frequency must be greater than 0.")

        response = _schedule_service.generate_schedule(request)
        logger.info(f"Successfully generated optimal scheduling slots for '{request.platform}'.")
        return response

    except ValueError as ve:
        logger.warning(f"Bad Request in analyze_schedule: {ve}")
        raise
    except Exception as e:
        logger.error(f"Unexpected execution error in analyze_schedule: {e}", exc_info=True)
        raise RuntimeError(f"Tool Execution Failed: Unable to recommend schedule -> {str(e)}")


scheduling_tool = FunctionTool(func=analyze_schedule)
