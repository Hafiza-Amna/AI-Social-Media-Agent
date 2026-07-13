import logging
from utils.tool_wrapper import FunctionTool
from models.competitor_request import CompetitorRequest
from models.competitor_response import CompetitorResponse
from services.competitor_analysis_service import CompetitorAnalysisService

logger = logging.getLogger(__name__)
_competitor_service = CompetitorAnalysisService()


def analyze_competitor(request: CompetitorRequest) -> CompetitorResponse:
    """
    Conducts deep competitive intelligence analysis to uncover market gaps, generate SWOT analyses,
    and produce actionable strategic recommendations.
    Provide a CompetitorRequest with the competitor's name, platform, metrics, and our brand profile.
    """
    logger.info(f"Executing 'analyze_competitor' for competitor '{request.competitor_name}' on '{request.platform}'.")

    try:
        if not request.competitor_name or not request.competitor_name.strip():
            raise ValueError("Validation Error: The competitor's name cannot be empty.")

        response = _competitor_service.analyze_competitor(request)
        logger.info(f"Competitor analysis complete. Threat Score: {response.overall_competitor_score}/100.")
        return response

    except ValueError as ve:
        logger.warning(f"Bad Request in analyze_competitor: {ve}")
        raise
    except Exception as e:
        logger.error(f"Unexpected execution error in analyze_competitor: {e}", exc_info=True)
        raise RuntimeError(f"Tool Execution Failed: Unable to perform competitor analysis -> {str(e)}")


competitor_tool = FunctionTool(func=analyze_competitor)
