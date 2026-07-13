from pydantic import BaseModel, Field
from typing import List
from datetime import date

class CalendarPost(BaseModel):
    """
    Model representing a single planned post within the content calendar.
    """
    scheduled_date: date = Field(..., description="The date the post should be published.")
    platform: str = Field(..., description="The specific platform for this post.")
    content_pillar: str = Field(..., description="The core content pillar or theme this post addresses.")
    post_topic: str = Field(..., description="A brief summary of what the post is about.")
    suggested_caption: str = Field(..., description="The fully drafted caption or main body text.")
    suggested_cta: str = Field(..., description="The specific Call to Action (CTA).")
    hashtag_set: List[str] = Field(..., description="A strategic set of relevant hashtags.")
    best_posting_time: str = Field(..., description="The empirically suggested optimal time of day to post (e.g., '10:00 AM EST').")
