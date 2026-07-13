import logging
from utils.tool_wrapper import FunctionTool
from models.analytics_request import AnalyticsRequest
from models.analytics_response import AnalyticsResponse
from services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)
_analytics_service = AnalyticsService()


def run_analytics(request: AnalyticsRequest) -> AnalyticsResponse:
    """
    Analyzes raw social media performance metrics to provide deep-dive strategic insights,
    trend predictions, and actionable recommendations.
    Provide an AnalyticsRequest with the target platform and the raw analytics data dictionary.
    """
    logger.info(f"Executing 'run_analytics' for platform '{request.platform}'.")

    try:
        if not request.analytics_data or len(request.analytics_data) == 0:
            raise ValueError("Validation Error: The raw analytics data payload cannot be empty.")

        response = _analytics_service.generate_report(request)
        logger.info(f"Analytics report generated. Account Health Score: {response.performance_score}/100.")
        return response

    except ValueError as ve:
        logger.warning(f"Bad Request in run_analytics: {ve}")
        raise
    except Exception as e:
        logger.error(f"Unexpected execution error in run_analytics: {e}", exc_info=True)
        raise RuntimeError(f"Tool Execution Failed: Unable to generate analytics report -> {str(e)}")


analytics_tool = FunctionTool(func=run_analytics)
