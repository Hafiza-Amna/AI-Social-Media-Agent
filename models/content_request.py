from pydantic import BaseModel, Field


class ContentRequest(BaseModel):
    """
    Model representing the input required to generate social media content.
    """

    topic: str = Field(
        ...,
        description="The main topic or subject of the post."
    )

    platform: str = Field(
        ...,
        description="Target platform. Allowed values: Instagram, Facebook, LinkedIn, X (Twitter)"
    )

    tone: str = Field(
        default="Professional yet engaging",
        description="The desired tone of the post."
    )

    target_audience: str = Field(
        ...,
        description="The primary audience for the content."
    )

    content_goal: str = Field(
        ...,
        description="The goal of the post (e.g., generate leads, brand awareness)."
    )

    language: str = Field(
        default="English",
        description="The language of the post."
    )

    number_of_variations: int = Field(
        default=1,
        ge=1,
        le=5,
        description="Number of content variations to generate."
    )