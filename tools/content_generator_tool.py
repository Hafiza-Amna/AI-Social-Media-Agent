import logging
from utils.tool_wrapper import FunctionTool
from models.content_request import ContentRequest
from models.content_response import ContentResponse
from services.content_generator import ContentGeneratorService

# Setup a dedicated logger for the tool execution
logger = logging.getLogger(__name__)

# Initialize the underlying business logic service as a singleton.
# This prevents re-initializing the Gemini client on every tool invocation.
_content_service = ContentGeneratorService()


def generate_content(request: ContentRequest) -> ContentResponse:
    """
    Generates highly engaging, platform-specific social media content.
    Provide a detailed ContentRequest including topic, platform, tone, and audience.
    """
    logger.info(f"Executing 'generate_content' for platform '{request.platform}'. Topic: '{request.topic}'")

    try:
        # 1. Validation Phase
        if not request.topic or not request.topic.strip():
            raise ValueError("Validation Error: The content topic cannot be empty.")

        if not request.target_audience or not request.target_audience.strip():
            raise ValueError("Validation Error: Target audience must be explicitly defined.")

        # 2. Execution Phase
        # Delegate the actual generation to the underlying clean-architecture service.
        response = _content_service.generate_content(request)

        logger.info(f"Successfully generated {len(response.variations)} content variations for '{request.platform}'.")

        # 3. Return Phase
        return response

    except ValueError as ve:
        logger.warning(f"Bad Request in generate_content: {ve}")
        raise
    except Exception as e:
        logger.error(f"Unexpected execution error in generate_content: {e}", exc_info=True)
        raise RuntimeError(f"Tool Execution Failed: Unable to generate content due to internal error -> {str(e)}")


# Wrap the plain Python function with Google ADK 2.3.0 FunctionTool.
# FunctionTool inspects the function signature and docstring to automatically build
# the JSON schema that the Gemini model uses for function calling / tool selection.
content_generator_tool = FunctionTool(func=generate_content)