from pydantic import BaseModel, Field
from typing import List
from models.calendar_post import CalendarPost

class CalendarResponse(BaseModel):
    """
    Model representing the final structured output of the content calendar generation.
    """
    posts: List[CalendarPost] = Field(..., description="A chronological list of the generated planned posts.")
