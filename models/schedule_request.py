from typing import Literal
from pydantic import BaseModel, Field


class ScheduleRequest(BaseModel):
    """
    Model representing the input required to determine optimal posting times 
    based on audience activity and content type.
    """

    platform: Literal[
        "linkedin",
        "instagram",
        "facebook",
        "twitter",
        "youtube"
    ] = Field(
        ...,
        description="The platform to post on."
    )

    timezone: str = Field(
        ...,
        description="The base timezone for scheduling."
    )

    audience_activity_data: str = Field(
        ...,
        description="A summary of historical audience activity."
    )

    content_type: str = Field(
        ...,
        description="The format of the content."
    )

    posting_frequency: int = Field(
        ...,
        description="The target number of posts per week."
    )