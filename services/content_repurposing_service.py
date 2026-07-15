"""
services/content_repurposing_service.py

Business logic for AI-powered cross-platform content repurposing.
The LLM provider is injected via the constructor.
"""
import logging
from models.repurpose_request import RepurposeRequest
from models.repurpose_response import RepurposeResponse
from prompts.content_repurposing_prompt import CONTENT_REPURPOSING_PROMPT
from utils.llm_provider import LLMProvider
from utils.provider_factory import get_llm_provider

logger = logging.getLogger(__name__)


class ContentRepurposingService:
    """
    Transforms a single piece of content into platform-native posts
    across multiple social networks.

    Dependency Injection
    --------------------
    Pass any ``LLMProvider`` to swap the underlying model::

        svc = ContentRepurposingService()                          # Production
        svc = ContentRepurposingService(llm_provider=MockProvider()) # Testing
    """

    def __init__(self, llm_provider: LLMProvider | None = None) -> None:
        self.llm_provider: LLMProvider = llm_provider or get_llm_provider()
        logger.debug(
            f"ContentRepurposingService initialised with provider: "
            f"{type(self.llm_provider).__name__}"
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def repurpose_content(self, request: RepurposeRequest) -> RepurposeResponse:
        """
        Returns platform-tailored posts, a quality score, and explanations.
        """
        targets_str = ", ".join(request.target_platforms)
        prompt = CONTENT_REPURPOSING_PROMPT.format(
            source_platform=request.source_platform,
            original_content=request.original_content,
            target_platforms=targets_str,
            tone=request.tone,
            target_audience=request.target_audience,
        )

        try:
            return self.llm_provider.generate_structured_output(
                prompt, RepurposeResponse, temperature=0.6
            )
        except Exception as exc:
            logger.error(f"ContentRepurposingService error: {exc}", exc_info=True)
            raise RuntimeError(f"Error during content repurposing generation: {exc}") from exc
