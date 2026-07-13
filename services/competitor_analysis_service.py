"""
services/competitor_analysis_service.py

Business logic for AI-powered competitive intelligence analysis.
The LLM provider is injected via the constructor.
"""
import json
import logging
from models.competitor_request import CompetitorRequest
from models.competitor_response import CompetitorResponse
from prompts.competitor_analysis_prompt import COMPETITOR_ANALYSIS_PROMPT
from services.brand_voice_service import BrandVoiceService
from utils.llm_provider import LLMProvider
from utils.provider_factory import get_llm_provider

logger = logging.getLogger(__name__)


class CompetitorAnalysisService:
    """
    Conducts deep competitive intelligence analysis — SWOT, market gaps,
    and strategic counter-recommendations.

    Dependency Injection
    --------------------
    Pass any ``LLMProvider`` to swap the underlying model::

        svc = CompetitorAnalysisService()                          # Production
        svc = CompetitorAnalysisService(llm_provider=MockProvider()) # Testing
    """

    def __init__(self, llm_provider: LLMProvider | None = None) -> None:
        self.llm_provider: LLMProvider = llm_provider or get_llm_provider()
        self.brand_voice_service = BrandVoiceService()
        logger.debug(
            f"CompetitorAnalysisService initialised with provider: "
            f"{type(self.llm_provider).__name__}"
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def analyze_competitor(self, request: CompetitorRequest) -> CompetitorResponse:
        """
        Returns a structured competitive intelligence report.
        """
        metrics_str = json.dumps(request.competitor_metrics, indent=2)
        brand_context = self.brand_voice_service.format_brand_context(request.our_brand_profile)
        prompt = COMPETITOR_ANALYSIS_PROMPT.format(
            platform=request.platform,
            competitor_name=request.competitor_name,
            competitor_metrics=metrics_str,
            brand_context=brand_context,
        )

        try:
            return self.llm_provider.generate_structured_output(
                prompt, CompetitorResponse, temperature=0.4
            )
        except Exception as exc:
            logger.error(f"CompetitorAnalysisService error: {exc}", exc_info=True)
            raise RuntimeError(f"Error during competitor analysis generation: {exc}") from exc
