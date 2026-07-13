import logging
from utils.tool_wrapper import FunctionTool
from models.calendar_request import CalendarRequest
from models.calendar_response import CalendarResponse
from services.content_calendar_service import ContentCalendarService

logger = logging.getLogger(__name__)
_calendar_service = ContentCalendarService()


def generate_calendar(request: CalendarRequest) -> CalendarResponse:
    """
    Generates a strategic, multi-day social media content calendar.
    Provide a CalendarRequest including brand profile, platform, content pillars, frequency, and campaign goal.
    """
    logger.info(f"Executing 'generate_calendar' for platform '{request.platform}'. Campaign Goal: '{request.campaign_goal}'")

    try:
        if request.duration_days <= 0:
            raise ValueError("Validation Error: Campaign duration must be greater than 0 days.")

        if not request.content_pillars or len(request.content_pillars) == 0:
            raise ValueError("Validation Error: At least one content pillar must be provided.")

        response = _calendar_service.generate_calendar(request)
        logger.info(f"Successfully generated a {request.duration_days}-day content calendar for '{request.platform}'.")
        return response

    except ValueError as ve:
        logger.warning(f"Bad Request in generate_calendar: {ve}")
        raise
    except Exception as e:
        logger.error(f"Unexpected execution error in generate_calendar: {e}", exc_info=True)
        raise RuntimeError(f"Tool Execution Failed: Unable to generate content calendar -> {str(e)}")


calendar_tool = FunctionTool(func=generate_calendar)
