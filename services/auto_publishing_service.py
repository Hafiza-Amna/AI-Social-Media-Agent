import uuid
from typing import List, Optional
from datetime import datetime
from models.publish_request import PublishRequest
from models.publish_job import PublishJob, PublishStatus
from models.publish_response import PublishResponse

class AutoPublishingService:
    """
    Service responsible for orchestrating the publishing queue.
    It handles scheduling, rescheduling, cancelling, and executing social media posts.
    """
    
    def __init__(self):
        # In a real app, this would be a database table (e.g., SQLite `publish_jobs`)
        # We use an in-memory dictionary here as a functional queue.
        self._queue = {}

    def schedule_post(self, request: PublishRequest) -> PublishResponse:
        """
        Accepts a finalized, scheduled post from the Smart Scheduler and adds it to the queue.
        """
        job_id = str(uuid.uuid4())
        
        new_job = PublishJob(
            job_id=job_id,
            platform=request.platform,
            account_id=request.account_id,
            scheduled_datetime=request.scheduled_datetime,
            content=request.content,
            media_placeholders=request.media_placeholders,
            status=PublishStatus.SCHEDULED
        )
        
        self._queue[job_id] = new_job
        
        return PublishResponse(
            success=True,
            message=f"Post successfully queued for {new_job.scheduled_datetime}.",
            job=new_job
        )

    def cancel_post(self, job_id: str) -> PublishResponse:
        """
        Aborts a scheduled post so it won't be published.
        """
        if job_id not in self._queue:
            raise ValueError("Job ID not found in the queue.")
            
        job = self._queue[job_id]
        if job.status in [PublishStatus.PUBLISHED, PublishStatus.CANCELLED]:
            return PublishResponse(
                success=False,
                message=f"Cannot cancel a job that is already {job.status.value}.",
                job=job
            )
            
        job.status = PublishStatus.CANCELLED
        return PublishResponse(
            success=True,
            message="Post has been successfully cancelled.",
            job=job
        )

    def reschedule_post(self, job_id: str, new_datetime: datetime) -> PublishResponse:
        """
        Updates the target execution time for an existing queued post.
        """
        if job_id not in self._queue:
            raise ValueError("Job ID not found in the queue.")
            
        job = self._queue[job_id]
        if job.status == PublishStatus.PUBLISHED:
            return PublishResponse(
                success=False,
                message="Cannot reschedule a post that has already been published.",
                job=job
            )
            
        job.scheduled_datetime = new_datetime
        # Reset the status to scheduled in case it was previously failed or pending
        job.status = PublishStatus.SCHEDULED 
        job.retry_count = 0
        job.error_message = None
        
        return PublishResponse(
            success=True,
            message=f"Post successfully rescheduled to {new_datetime}.",
            job=job
        )

    def execute_job(self, job_id: str) -> PublishResponse:
        """
        Simulates the chron job execution of publishing a post to the respective social platform.
        """
        if job_id not in self._queue:
            raise ValueError("Job ID not found in the queue.")
            
        job = self._queue[job_id]
        
        if job.status != PublishStatus.SCHEDULED:
            return PublishResponse(
                success=False,
                message=f"Job is not in a valid state to publish. Current state: {job.status.value}.",
                job=job
            )
            
        job.status = PublishStatus.PENDING
        
        try:
            # TODO: Integrate actual Social Media APIs using SocialAccountService for OAuth
            # Simulating a successful API call:
            job.status = PublishStatus.PUBLISHED
            return PublishResponse(
                success=True,
                message="Post successfully published to the target platform.",
                job=job
            )
        except Exception as e:
            # Handle API limits, network errors, or auth failures
            job.status = PublishStatus.FAILED
            job.error_message = str(e)
            job.retry_count += 1
            return PublishResponse(
                success=False,
                message=f"Failed to publish post: {str(e)}",
                job=job
            )

    def get_queue(self, status_filter: Optional[PublishStatus] = None) -> List[PublishJob]:
        """
        Retrieves all jobs in the publishing queue, optionally filtering by their current status.
        """
        if status_filter:
            return [job for job in self._queue.values() if job.status == status_filter]
        return list(self._queue.values())
