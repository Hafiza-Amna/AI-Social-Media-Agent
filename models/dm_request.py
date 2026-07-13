from pydantic import BaseModel, Field
from typing import List, Dict, Any


class DMRequest(BaseModel):
    """
    Model representing the input data required to generate an intelligent reply to a Direct Message.
    """
    incoming_message: str = Field(
        ...,
        description="The exact text of the latest incoming direct message."
    )
    conversation_history: List[Dict[str, str]] = Field(
        default_factory=list,
        description="A list of previous messages in the conversation for context (e.g., [{'role': 'user', 'content': 'hi'}])."
    )
    platform: str = Field(
        ...,
        description="The platform where the DM was received. Allowed values: Instagram, Facebook, LinkedIn, X (Twitter)"
    )
    brand_profile: Dict[str, Any] = Field(
        ...,
        description="The brand guidelines as a dictionary ensuring the reply matches the brand's unique voice. Keys include: brand_name, brand_description, industry, target_audience, writing_style, tone_of_voice, emoji_preference, cta_style."
    )
