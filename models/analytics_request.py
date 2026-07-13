from pydantic import BaseModel, Field
from typing import Dict, Any


class AnalyticsRequest(BaseModel):
    """
    Model representing the raw data input required to generate an AI analytics report.
    """
    platform: str = Field(
        ...,
        description="The platform the analytics correspond to. Allowed values: Instagram, Facebook, LinkedIn, X (Twitter)"
    )
    analytics_data: Dict[str, Any] = Field(
        ...,
        description="A dictionary of raw analytics data (e.g., likes, comments, shares, saves, impressions, reach, followers, engagement rate, and an array of individual post performance).",
    )
