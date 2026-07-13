from pydantic import BaseModel, Field
from typing import List

class RecommendedSlot(BaseModel):
    """
    Model representing a single recommended posting slot determined by the AI.
    """
    day_of_week: str = Field(..., description="The recommended day of the week to post.")
    time_of_day: str = Field(..., description="The recommended time of day in the requested timezone.")
    predicted_engagement_score: int = Field(..., ge=1, le=100, description="Predicted engagement score from 1-100.")
    reasoning: str = Field(..., description="Analytical explanation of why this time and day were recommended.")

class ScheduleResponse(BaseModel):
    """
    Model representing the AI's complete smart schedule recommendations.
    """
    recommended_slots: List[RecommendedSlot] = Field(..., description="A list of optimal posting slots based on the target frequency.")
    general_strategy: str = Field(..., description="Overall strategic advice considering the content type, timezone, and platform.")
