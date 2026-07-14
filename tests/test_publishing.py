import pytest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime

from config import settings
from services.auto_publishing_service import AutoPublishingService
from models.publish_request import PublishRequest
from models.publish_job import PublishJob, PublishStatus
from router import AIIntentRouter
from database import SessionLocal, Base, engine

# Setup test SQLite database
@pytest.fixture(autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def mock_settings():
    with patch("config.settings.LINKEDIN_ACCESS_TOKEN", "mock_token"):
        yield

def test_successful_linkedin_publishing_publish_post(mock_settings):
    """Test successful publishing via publish_post immediately."""
    service = AutoPublishingService()
    request = PublishRequest(
        platform="LinkedIn",
        scheduled_datetime="2026-07-14T12:00:00",
        content="Hello world!"
    )
    
    with patch("requests.get") as mock_get, patch("requests.post") as mock_post:
        # Mock profile URN retrieval
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {"id": "test_member_id"}
        mock_get.return_value = mock_get_response

        # Mock UGC Post creation
        mock_post_response = MagicMock()
        mock_post_response.status_code = 201
        mock_post_response.json.return_value = {"id": "urn:li:share:success_12345"}
        mock_post.return_value = mock_post_response

        response = service.publish_post(request)
        
        assert response.publishing_status == "Success"
        assert response.publication_id == "urn:li:share:success_12345"
        assert "Successfully published" in response.message

def test_successful_linkedin_publishing_execute_job(mock_settings):
    """Test successful publishing via scheduled job execution."""
    service = AutoPublishingService()
    request = PublishRequest(
        platform="LinkedIn",
        scheduled_datetime="2026-07-14T12:00:00",
        content="Hello scheduled world!"
    )
    
    # Schedule post first to create job in database
    schedule_res = service.schedule_post(request)
    job_id = schedule_res.job["job_id"]
    
    with patch("requests.get") as mock_get, patch("requests.post") as mock_post:
        # Mock profile URN retrieval
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {"id": "test_member_id"}
        mock_get.return_value = mock_get_response

        # Mock UGC Post creation
        mock_post_response = MagicMock()
        mock_post_response.status_code = 201
        mock_post_response.json.return_value = {"id": "urn:li:share:scheduled_12345"}
        mock_post.return_value = mock_post_response

        response = service.execute_job(job_id)
        
        assert response.success is True
        assert response.publishing_status == "Success"
        assert response.publication_id == "urn:li:share:scheduled_12345"
        
        # Verify DB state has updated to Published
        db = SessionLocal()
        job = db.query(PublishJob).filter(PublishJob.job_id == job_id).first()
        assert job.status == PublishStatus.PUBLISHED.value
        db.close()

def test_linkedin_publishing_401_unauthorized(mock_settings):
    """Test 401 Invalid Access Token error handling."""
    service = AutoPublishingService()
    request = PublishRequest(
        platform="LinkedIn",
        scheduled_datetime="2026-07-14T12:00:00",
        content="Hello world!"
    )
    
    with patch("requests.get") as mock_get, patch("requests.post") as mock_post:
        # Mock profile URN retrieval to succeed
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {"id": "test_member_id"}
        mock_get.return_value = mock_get_response

        # Mock UGC Post creation to return 401
        mock_post_response = MagicMock()
        mock_post_response.status_code = 401
        mock_post_response.text = "Unauthorized access token"
        mock_post.return_value = mock_post_response

        response = service.publish_post(request)
        
        assert response.publishing_status == "Failed"
        assert "token is invalid or expired" in response.message

def test_linkedin_publishing_403_forbidden(mock_settings):
    """Test 403 Permission Denied error handling."""
    service = AutoPublishingService()
    request = PublishRequest(
        platform="LinkedIn",
        scheduled_datetime="2026-07-14T12:00:00",
        content="Hello world!"
    )
    
    with patch("requests.get") as mock_get, patch("requests.post") as mock_post:
        # Mock profile URN retrieval succeeding
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {"id": "test_member_id"}
        mock_get.return_value = mock_get_response

        # Mock UGC Post creation returning 403
        mock_post_response = MagicMock()
        mock_post_response.status_code = 403
        mock_post_response.text = "Forbidden"
        mock_post.return_value = mock_post_response

        response = service.publish_post(request)
        
        assert response.publishing_status == "Failed"
        assert "permission denied" in response.message.lower()

def test_router_behavior_when_tool_fails():
    """Test that the router handles a failing tool call by returning an error message."""
    router = AIIntentRouter()
    
    # Mock the tool's inner function in the router's tools map directly
    with patch.object(router._tools_map["publish_post"], "func", side_effect=RuntimeError("Database Connection Timeout")):
        result = router._execute_tool("publish_post", json.dumps({
            "platform": "LinkedIn",
            "scheduled_datetime": "2026-07-14T12:00:00",
            "content": "Fail me!"
        }))
        
        data = json.loads(result)
        assert "error" in data
        assert "Tool execution failed" in data["error"]
        assert "Database Connection Timeout" in data["error"]
