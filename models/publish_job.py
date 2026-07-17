import json
from enum import Enum
from sqlalchemy import Column, String, Integer, DateTime
from database import Base

class PublishStatus(str, Enum):
    """
    Enum representing the lifecycle states of a publishing job.
    """
    PENDING = "Pending"       # Currently in the process of being sent to the API
    SCHEDULED = "Scheduled"   # Waiting for its optimal time to be published
    PUBLISHED = "published"   # Successfully sent to the social network
    FAILED = "Failed"         # Encountered an error during publishing
    CANCELLED = "Cancelled"   # Aborted by the user
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"

class PublishJob(Base):
    """
    SQLAlchemy Model representing a single job in the auto-publishing queue.
    """
    __tablename__ = "publish_jobs"

    job_id = Column(String, primary_key=True, index=True)
    platform = Column(String, nullable=False)
    account_id = Column(String, nullable=False)
    scheduled_datetime = Column(DateTime, nullable=False)
    content = Column(String, nullable=False)
    media_placeholders_json = Column(String, default="[]")
    status = Column(String, default="pending_review")
    retry_count = Column(Integer, default=0)
    error_message = Column(String, nullable=True)

    # Human approval fields
    reviewer = Column(String, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    review_action = Column(String, nullable=True)

    @property
    def media_placeholders(self):
        try:
            return json.loads(self.media_placeholders_json or "[]")
        except Exception:
            return []

    @media_placeholders.setter
    def media_placeholders(self, value):
        self.media_placeholders_json = json.dumps(value or [])

    def to_dict(self):
        return {
            "job_id": self.job_id,
            "platform": self.platform,
            "account_id": self.account_id,
            "scheduled_datetime": self.scheduled_datetime,
            "content": self.content,
            "media_placeholders": self.media_placeholders,
            "status": self.status,
            "retry_count": self.retry_count,
            "error_message": self.error_message,
            "reviewer": self.reviewer,
            "reviewed_at": self.reviewed_at,
            "review_action": self.review_action
        }
