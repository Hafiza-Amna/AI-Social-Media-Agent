from pydantic import BaseModel, Field
from typing import List, Dict, Any


class CompetitorRequest(BaseModel):
    """
    Model representing the input required to run an AI competitor analysis.
    """
    competitor_name: str = Field(
        ...,
        description="The name or handle of the competitor profile."
    )
    platform: str = Field(
        ...,
        description="The platform being analyzed. Allowed values: Instagram, Facebook, LinkedIn, X (Twitter)"
    )
    competitor_metrics: Dict[str, Any] = Field(
        ...,
        description="The competitor's metrics as a dictionary. Expected keys: followers (int), engagement_rate (float), posting_frequency (str), content_types (list of str), hashtags (list of str)."
    )
    our_brand_profile: Dict[str, Any] = Field(
        ...,
        description="Our brand profile as a dictionary for AI comparison. Keys include: brand_name, brand_description, industry, target_audience, writing_style, tone_of_voice."
    )
