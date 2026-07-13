from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from models.platform_type import PlatformType

class PublishStatus(str, Enum):
    """
    Enum representing the lifecycle states of a publishing job.
    """
    PENDING = "Pending"       # Currently in the process of being sent to the API
    SCHEDULED = "Scheduled"   # Waiting for its optimal time to be published
    PUBLISHED = "Published"   # Successfully sent to the social network
    FAILED = "Failed"         # Encountered an error during publishing
    CANCELLED = "Cancelled"   # Aborted by the user

class PublishJob(BaseModel):
    """
    Model representing a single job in the auto-publishing queue.
    """
    job_id: str = Field(..., description="Unique ID for this publishing job.")
    platform: PlatformType = Field(..., description="The platform to publish to.")
    account_id: str = Field(..., description="The specific social account ID to publish on.")
    scheduled_datetime: datetime = Field(..., description="The precise date and time the post is scheduled to go live.")
    
    content: str = Field(..., description="The full caption, text, and hashtags of the post.")
    media_placeholders: List[str] = Field(default_factory=list, description="Placeholders for images/videos attached to the post.")
    
    status: PublishStatus = Field(default=PublishStatus.SCHEDULED, description="The current status of the job.")
    retry_count: int = Field(default=0, description="Number of times the system has tried to publish this post after a failure.")
    error_message: Optional[str] = Field(None, description="The specific error message returned by the platform, if any.")
