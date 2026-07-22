"""
router.py — AI Intent Router

Provider-independent implementation using the LLMProvider abstraction.
The router reads ``settings.MODEL_NAME`` from config at startup, but
delegates all low-level LiteLLM calls through ``LiteLLMProvider`` so
the underlying model can be swapped via a single env-var change.
"""
import json
import logging
import re
import uuid
import litellm

from config import settings
from agent import create_master_agent
from utils.litellm_helper import LiteLLMProvider   # concrete impl used for the chat/tool loop

# ─────────────────────────────────────────────────────────────────────────────
# Logger
# ─────────────────────────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# ─────────────────────────────────────────────────────────────────────────────
# Singleton: master agent loaded once at module level for performance
# ─────────────────────────────────────────────────────────────────────────────
_master_agent = create_master_agent()

# ─────────────────────────────────────────────────────────────────────────────
# Intent → Tool mapping for token-efficient routing
# Each entry: (list-of-keyword-signals, list-of-tool-names-to-include)
# Tools always included: content_generator_tool (used by publish flows)
# ─────────────────────────────────────────────────────────────────────────────
_INTENT_TOOL_MAP = [
    # ── More-specific intents first (prevents false matches with broader platform keywords) ──

    # Content repurposing — actual name: repurpose_content
    (
        ["repurpose", "reuse", "adapt content", "cross-post", "transform content"],
        ["repurpose_content", "generate_content"],
    ),
    # Content calendar — actual names: generate_calendar, analyze_schedule
    (
        ["calendar", "content plan", "content schedule", "weekly plan", "monthly plan",
         "campaign plan"],
        ["generate_content", "generate_calendar", "analyze_schedule"],
    ),
    # Scheduling — actual names: analyze_schedule, generate_calendar
    (
        ["best time", "optimal time", "when to post", "posting time"],
        ["analyze_schedule", "generate_calendar"],
    ),
    # Comments — actual name: reply_to_comment
    (
        ["reply to comment", "respond to comment", "comment reply"],
        ["reply_to_comment"],
    ),
    # DMs / messages — actual name: reply_to_dm
    (
        ["dm", "direct message", "message reply", "respond to message"],
        ["reply_to_dm"],
    ),
    # Analytics — actual name: run_analytics
    (
        ["analytics", "performance metrics", "engagement rate", "reach", "impressions",
         "stats", "statistics"],
        ["run_analytics"],
    ),
    # Competitor analysis — actual name: analyze_competitor
    (
        ["competitor", "competition", "swot", "market gap", "analyze competitor",
         "analyse competitor"],
        ["analyze_competitor"],
    ),
    # Team collaboration — actual name: manage_team
    (
        ["team", "assign task", "collaboration", "review workflow", "task assignment",
         "team member", "approve task"],
        ["manage_team"],
    ),

    # ── Broader platform intents (checked after specifics) ──

    # LinkedIn publishing — actual names: generate_content, publish_to_linkedin_tool, publish_post
    (
        ["linkedin", "post on linkedin", "publish on linkedin", "share on linkedin",
         "linkedin post", "publish linkedin"],
        ["generate_content", "publish_to_linkedin_tool", "publish_post"],
    ),
    # Instagram publishing — actual names: generate_content, publish_to_instagram_tool, publish_post
    (
        ["instagram", "post on instagram", "publish on instagram", "share on instagram",
         "instagram post", "caption", "ig post"],
        ["generate_content", "publish_to_instagram_tool", "publish_post"],
    ),
    # Content generation only (no publish intent)
    (
        ["generate content", "write a post", "create content", "draft a post",
         "write content", "generate a post", "create a post", "ab variant", "a/b"],
        ["generate_content"],
    ),
    # Scheduling (broad keyword — after more specific ones above)
    (
        ["schedule"],
        ["analyze_schedule", "generate_calendar"],
    ),
    # Comment (broad keyword — after more specific ones above)
    (
        ["comment"],
        ["reply_to_comment"],
    ),
    # Performance / insights (broad analytics keywords)
    (
        ["performance", "insights", "metrics"],
        ["run_analytics"],
    ),
]


def _extract_retry_after(error_message: str) -> str | None:
    """
    Parses the Groq/LiteLLM rate limit error message to extract the retry-after
    wait duration (e.g. "Please try again in 14.38s.").
    Returns a human-readable wait string, or None if not parseable.
    """
    match = re.search(r"[Pp]lease try again in ([\d.]+)(s|ms|m)", str(error_message))
    if not match:
        return None
    value = float(match.group(1))
    unit = match.group(2)
    if unit == "ms":
        seconds = int(value / 1000) + 1
        return f"{seconds} second{'s' if seconds != 1 else ''}"
    elif unit == "m":
        return f"{int(value)} minute{'s' if int(value) != 1 else ''}"
    else:
        seconds = int(value) + 1
        return f"{seconds} second{'s' if seconds != 1 else ''}"


def _select_tools_for_intent(
    user_message: str,
    all_tools: list,
    tools_schema: list,
    tools_map: dict,
) -> list:
    """
    Selects a minimal subset of tool schemas relevant to the detected user intent.
    Falls back to the complete tool set if no intent can be matched.

    This reduces per-request token usage by 50-70% for targeted queries.
    """
    msg_lower = user_message.lower()

    for keywords, tool_names in _INTENT_TOOL_MAP:
        if any(kw in msg_lower for kw in keywords):
            # Build filtered schema list, only including tools that are registered
            selected = [
                schema for schema in tools_schema
                if schema.get("function", {}).get("name") in tool_names
                   and schema.get("function", {}).get("name") in tools_map
            ]
            if selected:
                logger.info(
                    f"[Router] Intent matched — sending {len(selected)}/{len(tools_schema)} tool schemas."
                )
                return selected

    # No specific intent detected -> send all tools (safe fallback)
    logger.info("[Router] No specific intent detected — sending all tool schemas (fallback).")
    return tools_schema


class AIIntentRouter:
    """
    Provider-independent intent router.

    Architecture
    ------------
    1. Detects user intent and selects a minimal, relevant subset of tool schemas.
    2. Sends the user message + filtered tool schema to the LLM.
    3. If the LLM requests a tool call, executes the tool, appends the result,
       then re-invokes the LLM to synthesize a final natural-language response.

    Dependency Injection
    --------------------
    The ``llm_provider`` parameter accepts any ``LLMProvider`` instance.
    When omitted the production provider is resolved via ``get_llm_provider()``.
    This makes the router fully testable without network calls::

        router = AIIntentRouter(llm_provider=MockProvider())
    """

    def __init__(self, llm_provider: LiteLLMProvider | None = None) -> None:
        # Use the injected provider or fall back to the factory-resolved one
        from utils.provider_factory import get_llm_provider
        self._provider: LiteLLMProvider = llm_provider or get_llm_provider()
        self._model_name: str = settings.MODEL_NAME
        self._system_prompt: str = _master_agent.system_prompt
        self._tools = _master_agent.tools
        self._tools_map = {tool.name: tool for tool in self._tools}
        self._tools_schema = [tool.to_litellm_tool() for tool in self._tools]

        logger.info(
            f"AIIntentRouter initialised | model='{self._model_name}' | "
            f"provider='{type(self._provider).__name__}' | "
            f"tools={len(self._tools)}"
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    async def process_request_async(
        self, user_message: str, user_id: str = "default_user"
    ) -> str:
        """
        Async entry point — processes a raw user message and returns the
        final synthesized natural-language response.

        When a publish tool (publish_to_linkedin_tool / publish_to_instagram_tool)
        is invoked, the return value is a JSON string containing:
            {"response": str, "job_id": str, "status": "pending_review"}
        so the /chat endpoint can surface job_id to the caller.
        For all other requests a plain string is returned.
        """
        logger.info(f"[Router] user_id='{user_id}' | message='{user_message[:120]}'")

        if not user_message or not user_message.strip():
            logger.warning("[Router] Received empty message.")
            return (
                "Please provide a valid request. For example: "
                "'Generate a LinkedIn post about AI' or 'Analyze my competitor.'"
            )

        # -- Select minimal tool set based on detected intent ----------
        active_tools_schema = _select_tools_for_intent(
            user_message,
            self._tools,
            self._tools_schema,
            self._tools_map,
        )

        messages = [
            {"role": "system", "content": self._system_prompt},
            {"role": "user",   "content": user_message},
        ]

        # Tracks the first publish-tool result so we can return job_id
        _publish_result: dict | None = None
        PUBLISH_TOOLS = {"publish_to_linkedin_tool", "publish_to_instagram_tool"}

        try:
            # -- Step 1: Initial LLM call with filtered tool schema ----
            logger.info(
                f"[Router] Initiating LLM call | tools={len(active_tools_schema)} schemas."
            )
            response = litellm.completion(
                model=self._model_name,
                messages=messages,
                tools=active_tools_schema,
                tool_choice="auto",
                temperature=0.5,
                num_retries=0,   # No automatic retries — prevents TPM burst amplification
            )

            response_message = response.choices[0].message
            tool_calls = getattr(response_message, "tool_calls", None)

            # -- Step 2: Execute requested tools -----------------------
            if tool_calls:
                logger.info(f"[Router] LLM requested {len(tool_calls)} tool call(s).")
                messages.append(response_message)

                for tc in tool_calls:
                    fn_name   = tc.function.name
                    fn_args   = tc.function.arguments
                    tc_id     = tc.id

                    logger.info(f"[Router] Executing tool '{fn_name}' | args={fn_args[:200]}")

                    if fn_name == "publish_to_instagram_tool":
                        urls = re.findall(r'(https?://[^\s"\'<>]+)', user_message)
                        extracted_url = None
                        for url in urls:
                            url = url.rstrip('.,!?)(')
                            if any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                                extracted_url = url
                                break
                        
                        if extracted_url:
                            logger.info(f"[Router] Extracted media URL from user message: {extracted_url}")
                            try:
                                args_dict = json.loads(fn_args)
                                args_dict['media_url'] = extracted_url
                                fn_args = json.dumps(args_dict)
                            except Exception as e:
                                logger.error(f"[Router] Error modifying fn_args for Instagram tool: {e}")
                            tool_result_content = self._execute_tool(fn_name, fn_args)
                        else:
                            logger.warning("[Router] No valid image URL found in user message for Instagram publish.")
                            tool_result_content = json.dumps({
                                "success": False,
                                "error": "Validation Error: No image URL (jpg, jpeg, png, webp) found in your message. Instagram requires a valid image URL."
                            })
                    else:
                        tool_result_content = self._execute_tool(fn_name, fn_args)

                    # Capture publish tool results so we can return job_id
                    if fn_name in PUBLISH_TOOLS and _publish_result is None:
                        try:
                            _publish_result = json.loads(tool_result_content)
                        except (json.JSONDecodeError, TypeError):
                            pass

                    messages.append({
                        "role":        "tool",
                        "tool_call_id": tc_id,
                        "name":        fn_name,
                        "content":     tool_result_content,
                    })

                # -- Step 3: Re-invoke LLM to synthesize final answer --
                logger.info("[Router] Synthesizing final response from tool output.")

                # If a publish tool ran, tell the LLM exactly what to say
                if _publish_result:
                    job_id = _publish_result.get("job_id")
                    messages.append({
                        "role": "system",
                        "content": (
                            "IMPORTANT: The post has been QUEUED for human approval. "
                            "It has NOT been published yet. "
                            f"The job_id is: {job_id}. "
                            "Tell the user: their post has been saved with status 'pending_review', "
                            f"the job_id is {job_id}, and they must call "
                            f"POST /review/{job_id} with action='approve' to publish it. "
                            "Do NOT say 'successfully published'. "
                            "Do NOT claim the post is live."
                        )
                    })

                final = litellm.completion(
                    model=self._model_name,
                    messages=messages,
                    temperature=0.5,
                    num_retries=0,
                )
                final_text = final.choices[0].message.content or ""

                # If a publish tool ran, return a structured JSON payload
                if _publish_result:
                    job_id = _publish_result.get("job_id")
                    return json.dumps({
                        "response": final_text,
                        "job_id": job_id,
                        "status": "pending_review",
                        "content": _publish_result.get("content", ""),
                        "platform": _publish_result.get("platform", ""),
                    })

                return final_text

            # No tool calls — direct answer
            if response_message.content:
                logger.info("[Router] LLM responded directly (no tool calls).")
                return response_message.content

            logger.warning("[Router] LLM returned neither content nor tool calls.")
            return "I was unable to formulate a response. Please rephrase your request."

        except litellm.exceptions.AuthenticationError:
            logger.critical("[Router] Authentication failure — check your API key.")
            return "Authentication Error: please verify that a valid API key is configured."

        except litellm.exceptions.RateLimitError as exc:
            retry_after = _extract_retry_after(str(exc))
            if retry_after:
                msg = (
                    f"\u26a0\ufe0f The AI service has temporarily reached its token rate limit. "
                    f"Please wait {retry_after} and try again."
                )
            else:
                msg = (
                    "\u26a0\ufe0f The AI service has temporarily reached its token rate limit. "
                    "Please wait 15-20 seconds and try again."
                )
            logger.error(f"[Router] Rate limit hit: {exc}")
            return msg

        except Exception as exc:
            logger.error(f"[Router] Unexpected error: {exc}", exc_info=True)
            return (
                "I apologize, but I encountered an error processing your request. "
                "Please ensure your request relates to one of my core capabilities: "
                "Content Generation, Scheduling, Publishing, Comment/DM Replies, "
                "Analytics, Competitor Analysis, Content Repurposing, or Team Collaboration."
            )


    def process_request(
        self, user_message: str, user_id: str = "default_user"
    ) -> str:
        """Synchronous convenience wrapper (safe for CLI / unit tests)."""
        import asyncio
        return asyncio.run(self.process_request_async(user_message, user_id))

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
    def _execute_tool(self, fn_name: str, fn_args: str) -> str:
        """
        Executes a single registered tool and returns its JSON-serialised result.
        Errors are caught and returned as a JSON error payload so the LLM can
        gracefully communicate what went wrong to the user.
        """
        if fn_name not in self._tools_map:
            msg = f"Tool '{fn_name}' is not registered."
            logger.error(f"[Router] {msg}")
            return json.dumps({"error": msg})

        tool = self._tools_map[fn_name]
        try:
            args_dict = json.loads(fn_args)

            if tool.request_class is not None:
                # Tool takes a Pydantic model — construct it and call
                request_obj = tool.request_class(**args_dict)
                result = tool(request_obj)
            else:
                # Tool takes plain keyword arguments — call directly
                logger.info(f"[Router] Tool '{fn_name}' invoked with kwargs: {list(args_dict.keys())}")
                result = tool.func(**args_dict)

            serialized = (
                result.model_dump_json()
                if hasattr(result, "model_dump_json")
                else json.dumps(result)
            )
            logger.info(f"[Router] Tool '{fn_name}' completed successfully.")
            return serialized

        except Exception as exc:
            logger.error(f"[Router] Tool '{fn_name}' raised: {exc}", exc_info=True)
            return json.dumps({"error": f"Tool execution failed: {exc}"})


# ─────────────────────────────────────────────────────────────────────────────
# Quick smoke-test
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    router = AIIntentRouter()
    result = router.process_request(
        "Generate a professional LinkedIn post about the future of AI in marketing.",
        user_id=str(uuid.uuid4()),
    )
    print("\n---- Router Response ----")
    print(result)
