"""
utils/litellm_helper.py

Concrete LLM provider implementation backed by LiteLLM.
Implements the LLMProvider interface; swap this class for any other
concrete implementation (e.g. OpenAIProvider, MockProvider) without
touching any service business logic.
"""
import os
import json
import logging
import litellm
from pydantic import BaseModel

from config import settings
from utils.llm_provider import LLMProvider

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# API key bootstrapping — done once at module import so LiteLLM can locate
# the right credentials regardless of execution order.
# ─────────────────────────────────────────────────────────────────────────────
def _bootstrap_api_keys() -> None:
    """Pushes all configured API keys into the environment for LiteLLM."""
    key_map = {
        "GROQ_API_KEY":       settings.GROQ_API_KEY,
        "OPENAI_API_KEY":     settings.OPENAI_API_KEY,
        "GEMINI_API_KEY":     settings.GEMINI_API_KEY,
        "OPENROUTER_API_KEY": settings.OPENROUTER_API_KEY,
    }
    for env_var, value in key_map.items():
        if value:
            os.environ[env_var] = value
            logger.debug(f"API key set for: {env_var}")

_bootstrap_api_keys()


class LiteLLMProvider(LLMProvider):
    """
    Production-grade LLM provider using LiteLLM as the unified gateway.

    Supports Groq, OpenAI, Gemini, Anthropic, OpenRouter and any other
    provider that LiteLLM routes to — change is a single env-var update.

    Features
    --------
    * Retry loop (up to MAX_ATTEMPTS outer iterations) with per-error
      back-off strategy.
    * LiteLLM's own ``num_retries`` handles transient network blips.
    * Typed exceptions mapped to human-readable RuntimeError messages so
      callers never need to import litellm directly.
    * Markdown code-fence stripping in case the model wraps JSON output.
    """

    MAX_ATTEMPTS: int = 3

    def __init__(self, model_name: str | None = None) -> None:
        self._model_name = model_name or settings.MODEL_NAME
        logger.info(f"LiteLLMProvider initialised with model='{self._model_name}'")

    # ------------------------------------------------------------------
    # Public API — satisfies the LLMProvider contract
    # ------------------------------------------------------------------
    def generate_structured_output(
        self,
        prompt: str,
        response_schema: type[BaseModel],
        temperature: float = 0.2,
    ) -> BaseModel:
        """
        Invokes the LLM and returns a validated Pydantic model.

        The model is prompted with both the user content and a JSON Schema
        definition so it can generate schema-conformant JSON.  The response
        is then parsed and validated via Pydantic before being returned.
        """
        logger.info(
            f"[LiteLLMProvider] Generating structured output | "
            f"model='{self._model_name}' | schema='{response_schema.__name__}' | "
            f"temperature={temperature}"
        )

        schema_json = json.dumps(response_schema.model_json_schema(), indent=2)
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an assistant that outputs structured data. "
                    "You MUST return a valid JSON object that strictly adheres "
                    "to the provided schema.  Do NOT include markdown fences, "
                    "preamble, or any text outside the JSON object."
                ),
            },
            {
                "role": "user",
                "content": f"{prompt}\n\nRequired JSON Schema:\n{schema_json}",
            },
        ]

        for attempt in range(1, self.MAX_ATTEMPTS + 1):
            try:
                response = litellm.completion(
                    model=self._model_name,
                    messages=messages,
                    response_format={"type": "json_object"},
                    temperature=temperature,
                    num_retries=2,          # LiteLLM internal transient-error retries
                )

                raw = response.choices[0].message.content.strip()
                raw = self._strip_markdown(raw)
                logger.debug(f"[LiteLLMProvider] Raw response (attempt {attempt}): {raw[:200]}")
                return response_schema.model_validate_json(raw)

            except litellm.exceptions.AuthenticationError as exc:
                logger.critical("Authentication failure — invalid API key.")
                raise RuntimeError(
                    f"LLM Authentication Error: check GROQ_API_KEY / "
                    f"MODEL_NAME in your .env file.  Detail: {exc}"
                ) from exc

            except litellm.exceptions.RateLimitError as exc:
                logger.warning(f"Rate limit hit (attempt {attempt}/{self.MAX_ATTEMPTS}).")
                if attempt == self.MAX_ATTEMPTS:
                    raise RuntimeError(
                        f"LLM Rate Limit exceeded after {self.MAX_ATTEMPTS} retries.  "
                        f"Detail: {exc}"
                    ) from exc

            except (litellm.exceptions.APIConnectionError, litellm.exceptions.APIError) as exc:
                logger.error(f"API/connection error (attempt {attempt}/{self.MAX_ATTEMPTS}): {exc}")
                if attempt == self.MAX_ATTEMPTS:
                    raise RuntimeError(
                        f"LLM API Error: could not reach provider.  Detail: {exc}"
                    ) from exc

            except (json.JSONDecodeError, Exception) as exc:
                logger.warning(
                    f"Response parsing error on attempt {attempt}: {exc}",
                    exc_info=isinstance(exc, Exception) and not isinstance(exc, json.JSONDecodeError),
                )
                if attempt == self.MAX_ATTEMPTS:
                    raise RuntimeError(
                        f"LLM returned unparseable output after {self.MAX_ATTEMPTS} "
                        f"attempts.  Detail: {exc}"
                    ) from exc

        # Should be unreachable, but satisfies the type checker.
        raise RuntimeError("LLM invocation failed for unknown reasons.")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _strip_markdown(text: str) -> str:
        """Removes surrounding markdown code fences if present."""
        if text.startswith("```"):
            lines = text.splitlines()
            # Drop the opening fence line and the closing fence line
            inner = lines[1:-1] if lines[-1].strip() == "```" else lines[1:]
            return "\n".join(inner).strip()
        return text


# ─────────────────────────────────────────────────────────────────────────────
# Module-level backward-compat shim
# Allows legacy call-sites that imported the free function to keep working
# without modification while the codebase transitions to full DI.
# ─────────────────────────────────────────────────────────────────────────────
_default_provider: LiteLLMProvider | None = None


def generate_structured_output(
    prompt: str,
    response_schema: type[BaseModel],
    temperature: float = 0.2,
) -> BaseModel:
    """
    Module-level convenience wrapper (backward-compatible).
    Delegates to a lazily created LiteLLMProvider singleton.
    Prefer injecting LLMProvider explicitly in new code.
    """
    global _default_provider
    if _default_provider is None:
        _default_provider = LiteLLMProvider()
    return _default_provider.generate_structured_output(prompt, response_schema, temperature)
