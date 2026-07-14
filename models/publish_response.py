from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PublishResponse(BaseModel):
    """
    Model representing the result of a publishing attempt (or simulation).
    """
    publishing_status: Optional[str] = Field(None, description="The outcome status (e.g., 'Success', 'Failed', 'Simulated').")
    platform: Optional[str] = Field(None, description="The platform that was targeted.")
    scheduled_time: Optional[datetime] = Field(None, description="The time the post was originally scheduled for.")
    message: str = Field(..., description="A detailed success or failure message describing the outcome.")
    publication_id: Optional[str] = Field(None, description="The unique ID returned by the platform upon successful publication.")

    # Fields returned by auto_publishing_service for queue management compatibility
    success: Optional[bool] = Field(None, description="Whether the operation succeeded.")
    job: Optional[dict] = Field(None, description="The serialized PublishJob metadata.")
