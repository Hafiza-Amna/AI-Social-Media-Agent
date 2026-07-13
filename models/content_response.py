from pydantic import BaseModel, Field
from typing import List

class PostContent(BaseModel):
    """
    Model representing a single variation of a generated social media post.
    """
    headline: str = Field(..., description="A catchy headline or hook.")
    main_post: str = Field(..., description="The main body of the social media post.")
    hashtags: List[str] = Field(..., description="A list of relevant hashtags.")
    call_to_action: str = Field(..., description="A clear call-to-action (CTA).")

class ContentResponse(BaseModel):
    """
    Model representing the final output returned by the content generator.
    """
    variations: List[PostContent] = Field(..., description="The generated post variations.")
