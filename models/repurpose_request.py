from pydantic import BaseModel, Field
from typing import List


class RepurposeRequest(BaseModel):
    """
    Model representing the input required to logically repurpose social media content.
    """
    original_content: str = Field(
        ...,
        description="The original textual content to be repurposed."
    )
    source_platform: str = Field(
        ...,
        description="The platform where the original content was published. Allowed values: Instagram, Facebook, LinkedIn, X (Twitter)"
    )
    target_platforms: List[str] = Field(
        ...,
        description="A list of target platforms to repurpose the content for. Allowed values: Instagram, Facebook, LinkedIn, X (Twitter)"
    )
    tone: str = Field(
        ...,
        description="The desired tonal guidelines for the repurposed content (e.g., 'Professional', 'Casual')."
    )
    target_audience: str = Field(
        ...,
        description="The primary audience for the repurposed content."
    )
