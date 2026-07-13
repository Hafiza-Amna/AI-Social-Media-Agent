from enum import Enum
from pydantic import BaseModel, Field
from typing import List
from models.comment_response import SentimentType

class IntentType(str, Enum):
    """Enum for categorizing the primary intent of a user's direct message."""
    INQUIRY = "Inquiry"
    COMPLAINT = "Complaint"
    SUPPORT = "Support"
    FEEDBACK = "Feedback"
    SALES = "Sales"
    GENERAL = "General"

class DMResponse(BaseModel):
    """
    Model representing the AI's deep analysis and suggested replies for a Direct Message.
    """
    detected_intent: IntentType = Field(..., description="The detected underlying intent of the user's message.")
    detected_sentiment: SentimentType = Field(..., description="The analyzed sentiment of the user's message.")
    suggested_replies: List[str] = Field(..., description="Three varied, highly brand-consistent reply suggestions.", min_length=3, max_length=3)
    requires_escalation: bool = Field(..., description="True if the conversation needs human intervention (e.g., complex support, escalated complaints, high-value sales).")
    confidence_score: int = Field(..., ge=1, le=100, description="The AI's confidence score in its analysis and generated replies (1-100).")
