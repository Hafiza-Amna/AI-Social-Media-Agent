from pydantic import BaseModel, Field
from typing import List

class SWOTAnalysis(BaseModel):
    """
    Model representing a standard SWOT analysis output.
    """
    strengths: List[str] = Field(..., description="Key strengths of the competitor.")
    weaknesses: List[str] = Field(..., description="Key weaknesses of the competitor.")
    opportunities: List[str] = Field(..., description="Market opportunities for our brand to exploit.")
    threats: List[str] = Field(..., description="Potential threats posed by this competitor.")

class CompetitorResponse(BaseModel):
    """
    Model representing the AI's deep competitive intelligence report and strategic recommendations.
    """
    overall_competitor_score: int = Field(..., ge=0, le=100, description="Overall threat and performance score of the competitor (0-100).")
    swot_analysis: SWOTAnalysis = Field(..., description="Detailed SWOT analysis comparing them against our brand.")
    content_gaps: List[str] = Field(..., description="Identified content topics, formats, or angles the competitor is missing.")
    trending_content_ideas: List[str] = Field(..., description="Specific, actionable content ideas designed to capture their audience.")
    hashtag_improvements: List[str] = Field(..., description="Strategic recommendations for hashtags to outrank or bypass the competitor.")
    growth_trend_prediction: str = Field(..., description="AI prediction of the competitor's short-term future growth trajectory.")
    ai_recommendations: List[str] = Field(..., description="Broad strategic AI recommendations for positioning our brand effectively.")
