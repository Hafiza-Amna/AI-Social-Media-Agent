"""
services/content_generator.py

Business logic for AI-powered social media content generation.
The LLM provider is injected via the constructor, making this service
fully decoupled from any specific LLM implementation.
"""
import logging
from models.content_request import ContentRequest
from models.content_response import ContentResponse
from prompts.content_generation_prompt import CONTENT_GENERATION_PROMPT
from utils.llm_provider import LLMProvider
from utils.provider_factory import get_llm_provider

logger = logging.getLogger(__name__)


class ContentGeneratorService:
    """
    Generates highly engaging, platform-specific social media content.

    Dependency Injection
    --------------------
    Pass any ``LLMProvider`` implementation to swap the underlying model
    without touching this class::

        # Production (uses config)
        svc = ContentGeneratorService()

        # Testing (inject a mock)
        svc = ContentGeneratorService(llm_provider=MockProvider())
    """

    def __init__(self, llm_provider: LLMProvider | None = None) -> None:
        self.llm_provider: LLMProvider = llm_provider or get_llm_provider()
        logger.debug(
            f"ContentGeneratorService initialised with provider: "
            f"{type(self.llm_provider).__name__}"
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def generate_content(self, request: ContentRequest) -> ContentResponse:
        """
        Generates social media content from a ContentRequest.
        Returns a strongly-typed ContentResponse model.
        """
        prompt = CONTENT_GENERATION_PROMPT.format(
            topic=request.topic,
            platform=request.platform,
            tone=request.tone,
            target_audience=request.target_audience,
            content_goal=request.content_goal,
            language=request.language,
            number_of_variations=request.number_of_variations,
        )

        try:
            return self.llm_provider.generate_structured_output(
                prompt, ContentResponse, temperature=0.7
            )
        except Exception as exc:
            logger.error(f"ContentGeneratorService error: {exc}", exc_info=True)
            raise RuntimeError(f"Error during content generation: {exc}") from exc
