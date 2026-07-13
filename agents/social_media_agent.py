from config import settings
from prompts.system_prompts import SOCIAL_MEDIA_MANAGER_PROMPT

class SocialMediaAgent:
    """
    LiteLLM-compatible Agent definition.
    """
    def __init__(self, name: str, description: str, system_prompt: str):
        self.name = name
        self.description = description
        self.system_prompt = system_prompt

def create_social_media_agent() -> SocialMediaAgent:
    """
    Initializes and returns the root Social Media Agent.
    """
    return SocialMediaAgent(
        name="social_media_agent",
        description="A specialized AI manager for social media content, scheduling, and strategy.",
        system_prompt=SOCIAL_MEDIA_MANAGER_PROMPT
    )
