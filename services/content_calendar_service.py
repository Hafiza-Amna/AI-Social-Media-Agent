"""
services/content_calendar_service.py

Business logic for AI-powered multi-day content calendar generation.
The LLM provider is injected via the constructor.
"""
import logging
from models.calendar_request import CalendarRequest
from models.calendar_response import CalendarResponse
from prompts.content_calendar_prompt import CONTENT_CALENDAR_PROMPT
from services.brand_voice_service import BrandVoiceService
from utils.llm_provider import LLMProvider
from utils.provider_factory import get_llm_provider

logger = logging.getLogger(__name__)


class ContentCalendarService:
    """
    Orchestrates AI-generated, holistic multi-day content calendars.

    Dependency Injection
    --------------------
    Pass any ``LLMProvider`` to swap the underlying model::

        svc = ContentCalendarService()                          # Production
        svc = ContentCalendarService(llm_provider=MockProvider()) # Testing
    """

    def __init__(self, llm_provider: LLMProvider | None = None) -> None:
        self.llm_provider: LLMProvider = llm_provider or get_llm_provider()
        self.brand_voice_service = BrandVoiceService()
        logger.debug(
            f"ContentCalendarService initialised with provider: "
            f"{type(self.llm_provider).__name__}"
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def generate_calendar(self, request: CalendarRequest) -> CalendarResponse:
        """
        Generates a structured, multi-post content calendar.
        Injects the brand profile to ensure content consistency.
        """
        brand_context = self.brand_voice_service.format_brand_context(request.brand_profile)
        pillars_str = ", ".join(request.content_pillars)

        prompt = CONTENT_CALENDAR_PROMPT.format(
            duration_days=request.duration_days,
            start_date=request.start_date.isoformat(),
            platform=request.platform,
            content_pillars=pillars_str,
            posting_frequency=request.posting_frequency,
            campaign_goal=request.campaign_goal,
            target_audience=request.target_audience,
            brand_context=brand_context,
        )

        try:
            return self.llm_provider.generate_structured_output(
                prompt, CalendarResponse, temperature=0.8
            )
        except Exception as exc:
            logger.error(f"ContentCalendarService error: {exc}", exc_info=True)
            raise RuntimeError(f"Error during calendar generation: {exc}") from exc
