"""
utils/provider_factory.py

Centralised factory for LLM provider instantiation.

Design
------
All callers that need an LLMProvider should call ``get_llm_provider()``.
The factory reads ``settings.LLM_PROVIDER`` (default: "litellm") and
returns the appropriate concrete implementation.

Adding a new provider
---------------------
1. Create a new class in utils/ that inherits from LLMProvider and
   implements ``generate_structured_output``.
2. Register it in the ``_PROVIDER_REGISTRY`` dict below.
3. Set ``LLM_PROVIDER=your_key`` in .env — no other code changes needed.
"""
import logging
from functools import lru_cache

from config import settings
from utils.llm_provider import LLMProvider

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Registry: maps the LLM_PROVIDER config value → a zero-arg factory callable
# that returns an LLMProvider instance.
# ─────────────────────────────────────────────────────────────────────────────
def _build_registry() -> dict[str, type]:
    """
    Lazily imports concrete providers to keep startup fast and avoid
    importing provider SDKs that are not in use.
    """
    from utils.litellm_helper import LiteLLMProvider
    return {
        "litellm": LiteLLMProvider,
        "groq":    LiteLLMProvider,   # Groq is accessed via LiteLLM gateway
        "openai":  LiteLLMProvider,
        "gemini":  LiteLLMProvider,
        "openrouter": LiteLLMProvider,
    }


@lru_cache(maxsize=1)
def get_llm_provider() -> LLMProvider:
    """
    Returns a cached singleton LLMProvider based on the current configuration.

    The singleton is application-scoped; it is created once at first call
    and reused across all DI injection sites.  This avoids the overhead of
    re-reading configuration and re-bootstrapping API keys on every request.

    To swap providers at runtime (e.g. in tests) call
    ``get_llm_provider.cache_clear()`` before calling again.
    """
    registry = _build_registry()
    provider_key = settings.LLM_PROVIDER.lower()

    if provider_key not in registry:
        available = ", ".join(registry.keys())
        raise ValueError(
            f"Unknown LLM_PROVIDER='{provider_key}'.  "
            f"Available providers: {available}"
        )

    provider_class = registry[provider_key]
    provider = provider_class()
    logger.info(
        f"[ProviderFactory] Resolved LLM_PROVIDER='{provider_key}' "
        f"→ {provider_class.__name__}"
    )
    return provider
