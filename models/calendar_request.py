from pydantic import BaseModel, Field
from typing import List

class CalendarRequest(BaseModel):
    """
    Model representing the input required to generate a complete content calendar.
    """

    brand_profile: str = Field(
        ...,
        description="Brand description or identity."
    )

    platform: str = Field(
        ...,
        description="Target platform (LinkedIn, Instagram, Facebook, X)."
    )

    content_pillars: List[str] = Field(
        ...,
        description="Main content themes."
    )

    posting_frequency: str = Field(
        ...,
        description="Posting frequency (Daily, Weekly, etc.)."
    )

    start_date: str = Field(
        ...,
        description="Start date in YYYY-MM-DD format."
    )

    duration_days: int = Field(
        default=7,
        ge=1,
        le=365,
        description="Number of days."
    )

    campaign_goal: str = Field(
        ...,
        description="Campaign objective."
    )

    target_audience: str = Field(
        ...,
        description="Target audience."
    )