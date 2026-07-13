from pydantic import BaseModel, Field
from typing import List, Optional

class BrandProfile(BaseModel):
    """
    Model representing a reusable brand profile for consistent content generation.
    """
    brand_name: str = Field(..., description="The official name of the brand.")
    brand_description: str = Field(..., description="A short description of what the brand does and stands for.")
    industry: str = Field(..., description="The industry or niche the brand operates in.")
    target_audience: str = Field(..., description="A detailed description of the brand's primary target audience.")
    writing_style: str = Field(..., description="The preferred writing style (e.g., conversational, academic, journalistic).")
    tone_of_voice: str = Field(..., description="The specific tone to use (e.g., humorous, empathetic, authoritative).")
    preferred_vocabulary: List[str] = Field(default_factory=list, description="Words or phrases frequently used by the brand.")
    words_to_avoid: List[str] = Field(default_factory=list, description="Words or phrases the brand never uses.")
    emoji_preference: str = Field(..., description="How emojis should be used (e.g., minimal, highly expressive, none).")
    cta_style: str = Field(..., description="How the brand typically structures Calls to Action (e.g., soft nudge, direct command).")
    brand_mission: Optional[str] = Field(None, description="The core mission statement of the brand.")
    brand_values: List[str] = Field(default_factory=list, description="Key values or principles the brand upholds.")
