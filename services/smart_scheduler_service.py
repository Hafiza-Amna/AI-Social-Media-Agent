"""
services/smart_scheduler_service.py (secondary scheduler — calendar-aware)

Determines optimal posting times from a generated content calendar.
The LLM provider is injected via the constructor.
"""
import logging
from models.schedule_request import ScheduleRequest
from models.schedule_response import ScheduleResponse
from prompts.smart_scheduler_prompt import SMART_SCHEDULER_PROMPT
from utils.llm_provider import LLMProvider
from utils.provider_factory import get_llm_provider

logger = logging.getLogger(__name__)


class SmartSchedulerService:
    """
    Analyzes a generated content calendar and determines mathematically
    optimal posting times based on audience demographics and platform algorithms.

    Dependency Injection
    --------------------
    Pass any ``LLMProvider`` to swap the underlying model::

        svc = SmartSchedulerService()                          # Production
        svc = SmartSchedulerService(llm_provider=MockProvider()) # Testing
    """

    def __init__(self, llm_provider: LLMProvider | None = None) -> None:
        self.llm_provider: LLMProvider = llm_provider or get_llm_provider()
        logger.debug(
            f"SmartSchedulerService initialised with provider: "
            f"{type(self.llm_provider).__name__}"
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def optimize_schedule(self, request: ScheduleRequest) -> ScheduleResponse:
        """
        Returns a structured ScheduleResponse with optimized timings.
        """
        calendar_data_str = request.calendar.model_dump_json(indent=2)
        days_str = ", ".join(request.preferred_posting_days)

        prompt = SMART_SCHEDULER_PROMPT.format(
            platform=request.platform,
            audience_location=request.audience_location,
            timezone=request.timezone,
            posting_frequency=request.posting_frequency,
            preferred_posting_days=days_str,
            engagement_goals=request.engagement_goals,
            calendar_data=calendar_data_str,
        )

        try:
            return self.llm_provider.generate_structured_output(
                prompt, ScheduleResponse, temperature=0.4
            )
        except Exception as exc:
            logger.error(f"SmartSchedulerService error: {exc}", exc_info=True)
            raise RuntimeError(f"Error during schedule optimization: {exc}") from exc
