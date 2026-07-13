"""
utils/tool_wrapper.py

Provider-independent function wrapper for LLM tool-calling.
Generates Groq/LiteLLM-compatible JSON schemas by resolving $defs inline.
"""
import copy
import inspect
import logging
from typing import Callable, Type, get_type_hints
from pydantic import BaseModel

logger = logging.getLogger(__name__)


def _resolve_refs(schema: dict, defs: dict) -> dict:
    """
    Recursively resolves all ``$ref`` pointers against the ``$defs`` map
    and removes ``$defs`` from the final output.  Also flattens ``anyOf``
    patterns that Pydantic generates for ``Optional[X]`` into a simpler
    representation that Groq's strict JSON-schema parser accepts.
    """
    if isinstance(schema, dict):
        # ── Handle $ref ────────────────────────────────────────────────
        if "$ref" in schema:
            ref_path = schema["$ref"]                     # e.g. "#/$defs/BrandProfile"
            ref_name = ref_path.rsplit("/", 1)[-1]
            if ref_name in defs:
                resolved = copy.deepcopy(defs[ref_name])
                # Carry over description from the referring field
                if "description" in schema:
                    resolved["description"] = schema["description"]
                return _resolve_refs(resolved, defs)
            # If we can't resolve the $ref, drop it to avoid Groq errors
            logger.warning(f"Unresolvable $ref '{ref_path}' — replaced with open object.")
            result = {"type": "object", "description": schema.get("description", "")}
            return result

        # ── Handle anyOf (Optional[X] pattern) ─────────────────────────
        if "anyOf" in schema:
            variants = schema["anyOf"]
            non_null = [v for v in variants if v != {"type": "null"} and v.get("type") != "null"]
            if len(non_null) == 1:
                # Optional[X] — keep only X and resolve it recursively
                resolved = _resolve_refs(copy.deepcopy(non_null[0]), defs)
                if "description" in schema:
                    resolved["description"] = schema["description"]
                if "default" in schema:
                    resolved["default"] = schema["default"]
                if "title" in schema:
                    resolved["title"] = schema["title"]
                return resolved
            # Multi-variant anyOf — resolve each branch
            schema = dict(schema)
            schema["anyOf"] = [_resolve_refs(copy.deepcopy(v), defs) for v in variants]
            return schema

        # ── Handle allOf (single-item wrapper Pydantic sometimes emits) ─
        if "allOf" in schema:
            items = schema["allOf"]
            if len(items) == 1:
                resolved = _resolve_refs(copy.deepcopy(items[0]), defs)
                if "description" in schema:
                    resolved["description"] = schema["description"]
                return resolved

        # ── Recurse into all other dict values ─────────────────────────
        return {k: _resolve_refs(v, defs) for k, v in schema.items() if k != "$defs"}

    if isinstance(schema, list):
        return [_resolve_refs(item, defs) for item in schema]

    return schema


class FunctionTool:
    """
    Lightweight, provider-independent wrapper around Python functions
    to auto-generate JSON schemas compatible with LiteLLM tool calling.

    Groq Compatibility
    ------------------
    ``to_litellm_tool()`` resolves ``$defs`` / ``$ref`` / ``anyOf``
    inline so the generated schema never contains pointer-based
    references that Groq's strict validator rejects.
    """

    def __init__(self, func: Callable):
        self.func = func
        self.name = func.__name__
        self.description = func.__doc__.strip() if func.__doc__ else f"Execute {self.name}"

        # Determine the request model from signature/type hints
        sig = inspect.signature(func)
        self.request_class: Type[BaseModel] | None = None

        for _name, param in sig.parameters.items():
            annotation = param.annotation
            if isinstance(annotation, type) and issubclass(annotation, BaseModel):
                self.request_class = annotation
                break

        if not self.request_class:
            hints = get_type_hints(func)
            for _name, annotation in hints.items():
                if isinstance(annotation, type) and issubclass(annotation, BaseModel):
                    self.request_class = annotation
                    break

    # ------------------------------------------------------------------
    # Schema generation
    # ------------------------------------------------------------------
    def to_litellm_tool(self) -> dict:
        """
        Converts the tool definition into the standard OpenAI/LiteLLM
        tool schema.  All ``$defs``, ``$ref``, and ``anyOf`` constructs
        are resolved inline for Groq compatibility.
        """
        if self.request_class:
            raw_schema = self.request_class.model_json_schema()
            defs = raw_schema.pop("$defs", {})

            # Resolve nested definitions recursively
            resolved = _resolve_refs(raw_schema, defs)

            parameters = {
                "type": "object",
                "properties": resolved.get("properties", {}),
                "required": resolved.get("required", []),
            }
        else:
            parameters = {"type": "object", "properties": {}}

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": parameters,
            },
        }

    # ------------------------------------------------------------------
    # Callable interface
    # ------------------------------------------------------------------
    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)
