from pydantic import BaseModel, Field
from typing import List
from models.platform_type import PlatformType

class RepurposedPost(BaseModel):
    """
    Model representing the repurposed content, perfectly optimized for a specific target platform.
    """
    target_platform: PlatformType = Field(..., description="The specific target platform for this variation.")
    caption: str = Field(..., description="The fully drafted, algorithm-optimized caption.")
    hashtags: List[str] = Field(..., description="A strategic list of relevant hashtags optimized for the platform.")
    cta: str = Field(..., description="A platform-appropriate Call to Action (CTA).")
    emoji_suggestions: List[str] = Field(..., description="Suggested emojis to include or use for visual formatting.")
    best_posting_time: str = Field(..., description="Suggested best time of day to post on this specific platform.")

class RepurposeResponse(BaseModel):
    """
    Model representing the complete, multi-platform output of the content repurposing engine.
    """
    repurposed_posts: List[RepurposedPost] = Field(..., description="The list of perfectly tailored platform-specific posts.")
    quality_score: int = Field(..., ge=1, le=100, description="AI assessment score of how well the original core meaning was preserved (1-100).")
    ai_explanation: str = Field(..., description="AI explanation of why specific structural and tonal changes were made for each platform.")
