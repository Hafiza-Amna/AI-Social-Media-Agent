"""
services/smart_schedule_service.py

Business logic for AI-powered optimal posting schedule recommendation.
The LLM provider is injected via the constructor.
"""
import logging
from models.schedule_request import ScheduleRequest
from models.schedule_response import ScheduleResponse
from prompts.smart_schedule_prompt import SMART_SCHEDULE_PROMPT
from utils.llm_provider import LLMProvider
from utils.provider_factory import get_llm_provider

logger = logging.getLogger(__name__)


class SmartScheduleService:
    """
    Analyzes audience activity and platform algorithms to recommend
    the best posting days and times.

    Dependency Injection
    --------------------
    Pass any ``LLMProvider`` to swap the underlying model::

        svc = SmartScheduleService()                          # Production
        svc = SmartScheduleService(llm_provider=MockProvider()) # Testing
    """

    def __init__(self, llm_provider: LLMProvider | None = None) -> None:
        self.llm_provider: LLMProvider = llm_provider or get_llm_provider()
        logger.debug(
            f"SmartScheduleService initialised with provider: "
            f"{type(self.llm_provider).__name__}"
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def generate_schedule(self, request: ScheduleRequest) -> ScheduleResponse:
        """
        Returns optimised posting slots and predicted engagement scores.
        """
        prompt = SMART_SCHEDULE_PROMPT.format(
            platform=request.platform,
            timezone=request.timezone,
            content_type=request.content_type,
            posting_frequency=request.posting_frequency,
            audience_activity_data=request.audience_activity_data,
        )

        try:
            return self.llm_provider.generate_structured_output(
                prompt, ScheduleResponse, temperature=0.3
            )
        except Exception as exc:
            logger.error(f"SmartScheduleService error: {exc}", exc_info=True)
            raise RuntimeError(f"Error during smart schedule generation: {exc}") from exc
