from enum import Enum
from pydantic import BaseModel, Field
from typing import List

class SentimentType(str, Enum):
    """Enum for categorizing the emotional tone of a comment."""
    POSITIVE = "Positive"
    NEUTRAL = "Neutral"
    NEGATIVE = "Negative"

class CommentResponse(BaseModel):
    """
    Model representing the AI's analysis and suggested replies for an incoming comment.
    """
    detected_sentiment: SentimentType = Field(..., description="The analyzed sentiment of the incoming comment.")
    suggested_replies: List[str] = Field(..., description="Three varied, highly brand-consistent reply suggestions.", min_length=3, max_length=3)
    requires_human_attention: bool = Field(..., description="True if the comment needs human escalation (e.g., severe complaints, legal issues, PR risks).")
    confidence_score: int = Field(..., ge=1, le=100, description="The AI's confidence score in its analysis and generated replies (1-100).")
