from pydantic import BaseModel, Field
from typing import List

class PostPerformance(BaseModel):
    """
    Model detailing the performance of a specific post.
    """
    post_identifier: str = Field(..., description="A short description or ID of the post.")
    reason: str = Field(..., description="Analytical reasoning explaining why this post succeeded or failed.")

class AnalyticsResponse(BaseModel):
    """
    Model representing the AI's deep analysis, insights, and strategic recommendations based on the analytics data.
    """
    performance_score: int = Field(..., ge=0, le=100, description="Overall AI-calculated performance score (0-100).")
    summary_report: str = Field(..., description="An executive summary report of the overall performance.")
    best_performing_posts: List[PostPerformance] = Field(..., description="Identification and analysis of the best-performing posts.")
    worst_performing_posts: List[PostPerformance] = Field(..., description="Identification and analysis of the worst-performing posts.")
    engagement_trends: str = Field(..., description="Analysis of identified engagement trends over the given dataset.")
    recommended_posting_time: str = Field(..., description="The mathematically AI-recommended best posting time based on the data.")
    recommended_content_type: str = Field(..., description="The AI-recommended best content type (e.g., Video, Carousel) based on historical success.")
    ai_improvements: List[str] = Field(..., description="A list of actionable, AI-powered suggestions for growth.")
    future_engagement_prediction: str = Field(..., description="A data-driven prediction of future engagement if current trends continue.")
