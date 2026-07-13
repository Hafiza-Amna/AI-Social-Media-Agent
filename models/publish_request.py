from pydantic import BaseModel, Field
from typing import List, Optional


class PublishRequest(BaseModel):
    """
    Model representing the payload required to trigger an auto-publishing job.
    """
    platform: str = Field(
        ...,
        description="The target platform for the post. Allowed values: Instagram, Facebook, LinkedIn, X (Twitter)"
    )
    scheduled_datetime: str = Field(
        ...,
        description="The precise date and time the post is scheduled for, in ISO 8601 format (e.g. 2025-01-15T10:30:00)."
    )
    content: str = Field(
        ...,
        description="The fully generated textual content of the post."
    )
    media_urls: List[str] = Field(
        default_factory=list,
        description="An optional list of media URLs (images, videos) to attach."
    )
