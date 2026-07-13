"""
services/analytics_service.py

Business logic for AI-powered social media analytics.
The LLM provider is injected via the constructor.
"""
import json
import logging
from models.analytics_request import AnalyticsRequest
from models.analytics_response import AnalyticsResponse
from prompts.analytics_prompt import ANALYTICS_PROMPT
from utils.llm_provider import LLMProvider
from utils.provider_factory import get_llm_provider

logger = logging.getLogger(__name__)


class AnalyticsService:
    """
    Deeply analyzes raw social media metrics and returns strategic insights.

    Dependency Injection
    --------------------
    Pass any ``LLMProvider`` implementation to swap the underlying model::

        svc = AnalyticsService()                          # Production
        svc = AnalyticsService(llm_provider=MockProvider()) # Testing
    """

    def __init__(self, llm_provider: LLMProvider | None = None) -> None:
        self.llm_provider: LLMProvider = llm_provider or get_llm_provider()
        logger.debug(
            f"AnalyticsService initialised with provider: "
            f"{type(self.llm_provider).__name__}"
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def generate_report(self, request: AnalyticsRequest) -> AnalyticsResponse:
        """
        Analyzes raw analytics data and returns scores, trends, and advice.
        """
        data_str = json.dumps(request.analytics_data, indent=2)
        prompt = ANALYTICS_PROMPT.format(
            platform=request.platform.value,
            analytics_data=data_str,
        )

        try:
            return self.llm_provider.generate_structured_output(
                prompt, AnalyticsResponse, temperature=0.2
            )
        except Exception as exc:
            logger.error(f"AnalyticsService error: {exc}", exc_info=True)
            raise RuntimeError(f"Error during AI analytics generation: {exc}") from exc
