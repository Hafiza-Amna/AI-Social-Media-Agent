from pydantic import BaseModel, Field
from typing import Dict, Any


class CommentRequest(BaseModel):
    """
    Model representing the input data required to generate an intelligent reply to a social media comment.
    """
    original_post: str = Field(
        ...,
        description="The content of the original social media post for context."
    )
    incoming_comment: str = Field(
        ...,
        description="The exact text of the incoming user comment to be analyzed."
    )
    platform: str = Field(
        ...,
        description="The platform where the comment was made. Allowed values: Instagram, Facebook, LinkedIn, X (Twitter)"
    )
    brand_profile: Dict[str, Any] = Field(
        ...,
        description="The brand guidelines as a dictionary ensuring the reply matches the brand's voice."
    )