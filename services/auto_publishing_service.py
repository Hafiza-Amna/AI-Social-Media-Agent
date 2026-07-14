import uuid
import logging
from typing import List, Optional
from datetime import datetime
from models.publish_request import PublishRequest
from models.publish_job import PublishJob, PublishStatus
from models.publish_response import PublishResponse
from database import SessionLocal, init_db

logger = logging.getLogger(__name__)

class AutoPublishingService:
    """
    Service responsible for orchestrating the publishing queue and executing posts.
    It handles scheduling, rescheduling, cancelling, immediate publishing, and executing social media posts.
    """
    
    def __init__(self):
        # Initialize SQLite database schema
        init_db()

    def schedule_post(self, request: PublishRequest) -> PublishResponse:
        """
        Accepts a finalized, scheduled post from the Smart Scheduler and adds it to the database queue.
        """
        try:
            scheduled_dt = datetime.fromisoformat(request.scheduled_datetime)
        except (ValueError, TypeError):
            scheduled_dt = datetime.utcnow()
            logger.warning(f"Could not parse scheduled_datetime '{request.scheduled_datetime}', defaulting to now.")

        job_id = str(uuid.uuid4())
        
        new_job = PublishJob(
            job_id=job_id,
            platform=request.platform,
            account_id=getattr(request, "account_id", "default_account"),
            scheduled_datetime=scheduled_dt,
            content=request.content,
            status=PublishStatus.SCHEDULED.value
        )
        new_job.media_placeholders = getattr(request, "media_placeholders", getattr(request, "media_urls", []))
        
        db = SessionLocal()
        try:
            db.add(new_job)
            db.commit()
            db.refresh(new_job)
            job_dict = new_job.to_dict()
        finally:
            db.close()
        
        return PublishResponse(
            success=True,
            message=f"Post successfully queued for {scheduled_dt}.",
            job=job_dict
        )

    def cancel_post(self, job_id: str) -> PublishResponse:
        """
        Aborts a scheduled post so it won't be published.
        """
        db = SessionLocal()
        try:
            job = db.query(PublishJob).filter(PublishJob.job_id == job_id).first()
            if not job:
                raise ValueError("Job ID not found in the database.")
                
            if job.status in [PublishStatus.PUBLISHED.value, PublishStatus.CANCELLED.value]:
                return PublishResponse(
                    success=False,
                    message=f"Cannot cancel a job that is already {job.status}.",
                    job=job.to_dict()
                )
                
            job.status = PublishStatus.CANCELLED.value
            db.commit()
            db.refresh(job)
            return PublishResponse(
                success=True,
                message="Post has been successfully cancelled.",
                job=job.to_dict()
            )
        finally:
            db.close()

    def reschedule_post(self, job_id: str, new_datetime: datetime) -> PublishResponse:
        """
        Updates the target execution time for an existing queued post.
        """
        db = SessionLocal()
        try:
            job = db.query(PublishJob).filter(PublishJob.job_id == job_id).first()
            if not job:
                raise ValueError("Job ID not found in the database.")
                
            if job.status == PublishStatus.PUBLISHED.value:
                return PublishResponse(
                    success=False,
                    message="Cannot reschedule a post that has already been published.",
                    job=job.to_dict()
                )
                
            job.scheduled_datetime = new_datetime
            # Reset the status to scheduled in case it was previously failed or pending
            job.status = PublishStatus.SCHEDULED.value 
            job.retry_count = 0
            job.error_message = None
            db.commit()
            db.refresh(job)
            return PublishResponse(
                success=True,
                message=f"Post successfully rescheduled to {new_datetime}.",
                job=job.to_dict()
            )
        finally:
            db.close()

    def execute_job(self, job_id: str) -> PublishResponse:
        """
        Executes a scheduled job from the database queue. If the platform is LinkedIn,
        it uses the real LinkedIn service, otherwise simulates the API posting process.
        """
        db = SessionLocal()
        try:
            job = db.query(PublishJob).filter(PublishJob.job_id == job_id).first()
            if not job:
                raise ValueError("Job ID not found in the database.")
                
            if job.status != PublishStatus.SCHEDULED.value:
                return PublishResponse(
                    success=False,
                    message=f"Job is not in a valid state to publish. Current state: {job.status}.",
                    job=job.to_dict()
                )
                
            job.status = PublishStatus.PENDING.value
            db.commit()
            db.refresh(job)
            
            platform_lower = job.platform.lower().strip()
            if platform_lower == "linkedin":
                from config import settings
                if not settings.LINKEDIN_ACCESS_TOKEN:
                    raise RuntimeError("LINKEDIN_ACCESS_TOKEN is missing or empty in settings.")
                
                logger.info("Executing real publishing to LinkedIn API via execute_job...")
                from services.linkedin_service import LinkedInService
                linkedin_service = LinkedInService()
                publication_id = linkedin_service.publish_text_post(job.content)
                
                job.status = PublishStatus.PUBLISHED.value
                job.error_message = None
                db.commit()
                db.refresh(job)
                
                return PublishResponse(
                    success=True,
                    message="Successfully published post to LinkedIn.",
                    job=job.to_dict(),
                    publishing_status="Success",
                    platform=job.platform,
                    scheduled_time=job.scheduled_datetime,
                    publication_id=publication_id
                )
            else:
                # Simulated publish for other platforms
                job.status = PublishStatus.PUBLISHED.value
                job.error_message = None
                db.commit()
                db.refresh(job)
                
                return PublishResponse(
                    success=True,
                    message=f"Successfully simulated publishing to {job.platform}.",
                    job=job.to_dict(),
                    publishing_status="Success (Simulated)",
                    platform=job.platform,
                    scheduled_time=job.scheduled_datetime,
                    publication_id=f"simulated_{job.job_id[:8]}"
                )

        except Exception as e:
            logger.error(f"Failed to execute job {job_id}: {e}", exc_info=True)
            if 'job' in locals() and job:
                job.status = PublishStatus.FAILED.value
                job.error_message = str(e)
                job.retry_count += 1
                db.commit()
                db.refresh(job)
                job_dict = job.to_dict()
            else:
                job_dict = None
                
            return PublishResponse(
                success=False,
                message=f"Failed to publish post: {str(e)}",
                job=job_dict,
                publishing_status="Failed",
                platform=job.platform if ('job' in locals() and job) else "Unknown",
                scheduled_time=job.scheduled_datetime if ('job' in locals() and job) else datetime.utcnow(),
                publication_id=None
            )
        finally:
            db.close()

    def get_queue(self, status_filter: Optional[PublishStatus] = None) -> List[dict]:
        """
        Retrieves all jobs in the publishing queue, optionally filtering by their current status.
        """
        db = SessionLocal()
        try:
            query = db.query(PublishJob)
            if status_filter:
                query = query.filter(PublishJob.status == status_filter.value)
            jobs = query.all()
            return [job.to_dict() for job in jobs]
        finally:
            db.close()

    def publish_post(self, request: PublishRequest) -> PublishResponse:
        """
        Validates the publishing request and simulates the API posting process immediately,
        or performs a real publish for LinkedIn.
        """
        try:
            scheduled_dt = datetime.fromisoformat(request.scheduled_datetime)
        except (ValueError, TypeError):
            scheduled_dt = datetime.utcnow()
            logger.warning(f"Could not parse scheduled_datetime '{request.scheduled_datetime}', defaulting to now.")

        # 1. Validation Phase
        if not request.content or request.content.strip() == "":
            return PublishResponse(
                publishing_status="Failed",
                platform=request.platform,
                scheduled_time=scheduled_dt,
                message="Validation Error: Post content cannot be empty.",
                publication_id=None
            )

        if scheduled_dt < datetime.utcnow():
            logger.warning("Scheduled time is in the past. Executing immediately as a catch-up post.")

        # 2. Execution Phase
        platform_lower = request.platform.lower().strip()
        
        if platform_lower == "linkedin":
            from config import settings
            if not settings.LINKEDIN_ACCESS_TOKEN:
                logger.error("LinkedIn access token is missing in configuration.")
                return PublishResponse(
                    publishing_status="Failed",
                    platform=request.platform,
                    scheduled_time=scheduled_dt,
                    message="Configuration Error: LINKEDIN_ACCESS_TOKEN is missing or empty in your environment/settings.",
                    publication_id=None
                )
            
            try:
                logger.info("Executing real publishing to LinkedIn API...")
                from services.linkedin_service import LinkedInService
                linkedin_service = LinkedInService()
                publication_id = linkedin_service.publish_text_post(request.content)
                
                return PublishResponse(
                    publishing_status="Success",
                    platform=request.platform,
                    scheduled_time=scheduled_dt,
                    message="Successfully published post to LinkedIn.",
                    publication_id=publication_id
                )
            except Exception as e:
                logger.error(f"Failed to publish to LinkedIn: {e}", exc_info=True)
                return PublishResponse(
                    publishing_status="Failed",
                    platform=request.platform,
                    scheduled_time=scheduled_dt,
                    message=f"LinkedIn Publishing Error: {str(e)}",
                    publication_id=None
                )
        
        # Fallback simulation for other platforms (e.g. Instagram, Facebook, X)
        logger.info(f"Simulating publishing to {request.platform}...")
        logger.debug(f"Content: {request.content}")
        media_urls = getattr(request, "media_urls", [])
        if media_urls:
            logger.debug(f"Media attached: {len(media_urls)} items.")

        # Generate a simulated publication ID
        platform_slug = request.platform.lower().replace(" ", "_").replace("(", "").replace(")", "")
        simulated_pub_id = f"{platform_slug}_post_{uuid.uuid4().hex[:8]}"

        return PublishResponse(
            publishing_status="Success (Simulated)",
            platform=request.platform,
            scheduled_time=scheduled_dt,
            message=f"Successfully simulated publishing to {request.platform}.",
            publication_id=simulated_pub_id
        )
