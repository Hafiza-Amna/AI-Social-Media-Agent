"""
utils — Application-level utilities and LLM provider infrastructure.

Public API
----------
LLMProvider       : Abstract base class / interface for all LLM providers.
LiteLLMProvider   : Concrete implementation backed by the LiteLLM gateway.
get_llm_provider  : Factory function — returns the configured singleton provider.
FunctionTool      : LiteLLM-compatible tool wrapper with auto JSON-schema generation.
"""
from utils.llm_provider import LLMProvider
from utils.litellm_helper import LiteLLMProvider
from utils.provider_factory import get_llm_provider
from utils.tool_wrapper import FunctionTool

__all__ = [
    "LLMProvider",
    "LiteLLMProvider",
    "get_llm_provider",
    "FunctionTool",
]
