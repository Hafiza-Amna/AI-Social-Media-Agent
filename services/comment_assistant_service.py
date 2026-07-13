"""
services/comment_assistant_service.py

Business logic for AI-powered social media comment analysis and reply generation.
The LLM provider is injected via the constructor.
"""
import logging
from models.comment_request import CommentRequest
from models.comment_response import CommentResponse
from prompts.comment_assistant_prompt import COMMENT_ASSISTANT_PROMPT
from services.brand_voice_service import BrandVoiceService
from utils.llm_provider import LLMProvider
from utils.provider_factory import get_llm_provider

logger = logging.getLogger(__name__)


class CommentAssistantService:
    """
    Analyzes incoming social media comments and generates brand-aligned replies.

    Dependency Injection
    --------------------
    Pass any ``LLMProvider`` implementation to swap the underlying model::

        svc = CommentAssistantService()                          # Production
        svc = CommentAssistantService(llm_provider=MockProvider()) # Testing
    """

    def __init__(self, llm_provider: LLMProvider | None = None) -> None:
        self.llm_provider: LLMProvider = llm_provider or get_llm_provider()
        self.brand_voice_service = BrandVoiceService()
        logger.debug(
            f"CommentAssistantService initialised with provider: "
            f"{type(self.llm_provider).__name__}"
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def generate_reply(self, request: CommentRequest) -> CommentResponse:
        """
        Analyzes an incoming comment and returns sentiment, replies, and escalation flags.
        """
        brand_context = self.brand_voice_service.format_brand_context(request.brand_profile)
        prompt = COMMENT_ASSISTANT_PROMPT.format(
            platform=request.platform,
            original_post=request.original_post,
            incoming_comment=request.incoming_comment,
            brand_context=brand_context,
        )

        try:
            return self.llm_provider.generate_structured_output(
                prompt, CommentResponse, temperature=0.6
            )
        except Exception as exc:
            logger.error(f"CommentAssistantService error: {exc}", exc_info=True)
            raise RuntimeError(
                f"Error during comment analysis and reply generation: {exc}"
            ) from exc
