"""
services/dm_assistant_service.py

Business logic for AI-powered Direct Message analysis and reply generation.
The LLM provider is injected via the constructor.
"""
import json
import logging
from models.dm_request import DMRequest
from models.dm_response import DMResponse
from prompts.dm_assistant_prompt import DM_ASSISTANT_PROMPT
from services.brand_voice_service import BrandVoiceService
from utils.llm_provider import LLMProvider
from utils.provider_factory import get_llm_provider

logger = logging.getLogger(__name__)


class DMAssistantService:
    """
    Deeply analyzes incoming DMs, determines user intent, and generates
    context-aware reply suggestions.

    Dependency Injection
    --------------------
    Pass any ``LLMProvider`` to swap the underlying model::

        svc = DMAssistantService()                          # Production
        svc = DMAssistantService(llm_provider=MockProvider()) # Testing
    """

    def __init__(self, llm_provider: LLMProvider | None = None) -> None:
        self.llm_provider: LLMProvider = llm_provider or get_llm_provider()
        self.brand_voice_service = BrandVoiceService()
        logger.debug(
            f"DMAssistantService initialised with provider: "
            f"{type(self.llm_provider).__name__}"
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def generate_reply(self, request: DMRequest) -> DMResponse:
        """
        Returns intent, sentiment, reply suggestions, and escalation flags.
        """
        brand_context = self.brand_voice_service.format_brand_context(request.brand_profile)
        history_str = (
            json.dumps(request.conversation_history, indent=2)
            if request.conversation_history
            else "No previous history."
        )

        prompt = DM_ASSISTANT_PROMPT.format(
            platform=request.platform,
            conversation_history=history_str,
            incoming_message=request.incoming_message,
            brand_context=brand_context,
        )

        try:
            return self.llm_provider.generate_structured_output(
                prompt, DMResponse, temperature=0.5
            )
        except Exception as exc:
            logger.error(f"DMAssistantService error: {exc}", exc_info=True)
            raise RuntimeError(
                f"Error during DM analysis and reply generation: {exc}"
            ) from exc
