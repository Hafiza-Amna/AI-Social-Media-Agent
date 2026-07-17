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
from fastapi.testclient import TestClient
from app import app

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

@pytest.fixture
def mock_instagram_settings():
    with patch("config.settings.IG_ACCESS_TOKEN", "mock_ig_token"), \
         patch("config.settings.IG_BUSINESS_ACCOUNT_ID", "123456789"):
        yield

def approve_job_in_db(job_id):
    db = SessionLocal()
    job = db.query(PublishJob).filter(PublishJob.job_id == job_id).first()
    job.status = PublishStatus.APPROVED.value
    db.commit()
    db.close()

# ─────────────────────────────────────────────────────────────────────────────
# LinkedIn Tests (existing adapted for approval workflow)
# ─────────────────────────────────────────────────────────────────────────────

def test_successful_linkedin_publishing_publish_post(mock_settings):
    """Test successful publishing via publish_post immediately after approval."""
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
        assert response.publishing_status == "pending_review"
        
        job_id = response.job["job_id"]
        approve_job_in_db(job_id)
        
        exec_res = service.execute_job(job_id)
        assert exec_res.success is True
        assert exec_res.publishing_status == "Success"
        assert exec_res.publication_id == "urn:li:share:success_12345"
        assert "Successfully published" in exec_res.message

def test_successful_linkedin_publishing_execute_job(mock_settings):
    """Test successful publishing via scheduled job execution after approval."""
    service = AutoPublishingService()
    request = PublishRequest(
        platform="LinkedIn",
        scheduled_datetime="2026-07-14T12:00:00",
        content="Hello scheduled world!"
    )
    
    # Schedule post first to create job in database
    schedule_res = service.schedule_post(request)
    job_id = schedule_res.job["job_id"]
    
    approve_job_in_db(job_id)
    
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
    """Test 401 Invalid Access Token error handling after approval."""
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
        job_id = response.job["job_id"]
        approve_job_in_db(job_id)
        
        exec_res = service.execute_job(job_id)
        assert exec_res.success is False
        assert exec_res.publishing_status == "Failed"
        assert "token is invalid or expired" in exec_res.message

def test_linkedin_publishing_403_forbidden(mock_settings):
    """Test 403 Permission Denied error handling after approval."""
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
        job_id = response.job["job_id"]
        approve_job_in_db(job_id)
        
        exec_res = service.execute_job(job_id)
        assert exec_res.success is False
        assert exec_res.publishing_status == "Failed"
        assert "permission denied" in exec_res.message.lower()

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


# ─────────────────────────────────────────────────────────────────────────────
# Instagram Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_instagram_publish_success(mock_instagram_settings):
    """Test successful Instagram publishing after approval."""
    service = AutoPublishingService()
    request = PublishRequest(
        platform="Instagram",
        scheduled_datetime="2026-07-14T12:00:00",
        content="Check out this photo! #AI #SocialMedia",
        media_urls=["https://example.com/photo.jpg"]
    )

    with patch("requests.post") as mock_post:
        # Mock Step 1: create media container
        container_response = MagicMock()
        container_response.status_code = 200
        container_response.json.return_value = {"id": "container_abc123"}

        # Mock Step 2: publish media container
        publish_response = MagicMock()
        publish_response.status_code = 200
        publish_response.json.return_value = {"id": "media_xyz789"}

        mock_post.side_effect = [container_response, publish_response]

        response = service.publish_post(request)
        job_id = response.job["job_id"]
        approve_job_in_db(job_id)
        
        exec_res = service.execute_job(job_id)
        assert exec_res.success is True
        assert exec_res.publishing_status == "Success"
        assert exec_res.publication_id == "media_xyz789"
        assert "Successfully published post to Instagram" in exec_res.message


def test_instagram_invalid_token(mock_instagram_settings):
    """Test Instagram 401 / invalid token error handling after approval."""
    service = AutoPublishingService()
    request = PublishRequest(
        platform="Instagram",
        scheduled_datetime="2026-07-14T12:00:00",
        content="Token test post",
        media_urls=["https://example.com/photo.jpg"]
    )

    with patch("requests.post") as mock_post:
        # Simulate API returning token error (code 190)
        error_response = MagicMock()
        error_response.status_code = 400
        error_response.json.return_value = {
            "error": {
                "message": "Invalid OAuth access token",
                "code": 190
            }
        }
        mock_post.return_value = error_response

        response = service.publish_post(request)
        job_id = response.job["job_id"]
        approve_job_in_db(job_id)
        
        exec_res = service.execute_job(job_id)
        assert exec_res.success is False
        assert exec_res.publishing_status == "Failed"
        assert "token is invalid or expired" in exec_res.message.lower()


def test_instagram_permission_denied(mock_instagram_settings):
    """Test Instagram permission denied (403 / code 10) error handling after approval."""
    service = AutoPublishingService()
    request = PublishRequest(
        platform="Instagram",
        scheduled_datetime="2026-07-14T12:00:00",
        content="Permission test post",
        media_urls=["https://example.com/photo.jpg"]
    )

    with patch("requests.post") as mock_post:
        # Simulate API returning a permissions error (code 10)
        error_response = MagicMock()
        error_response.status_code = 403
        error_response.json.return_value = {
            "error": {
                "message": "Application does not have permission for this action",
                "code": 10
            }
        }
        mock_post.return_value = error_response

        response = service.publish_post(request)
        job_id = response.job["job_id"]
        approve_job_in_db(job_id)
        
        exec_res = service.execute_job(job_id)
        assert exec_res.success is False
        assert exec_res.publishing_status == "Failed"
        assert "permission denied" in exec_res.message.lower()


def test_instagram_publish_success_via_execute_job(mock_instagram_settings):
    """Test successful Instagram publishing via scheduled job execution."""
    service = AutoPublishingService()
    request = PublishRequest(
        platform="Instagram",
        scheduled_datetime="2026-07-14T12:00:00",
        content="Scheduled Instagram post! #scheduled",
        media_urls=["https://example.com/photo.jpg"]
    )

    schedule_res = service.schedule_post(request)
    job_id = schedule_res.job["job_id"]
    approve_job_in_db(job_id)

    with patch("requests.post") as mock_post:
        container_response = MagicMock()
        container_response.status_code = 200
        container_response.json.return_value = {"id": "container_sched_001"}

        publish_response = MagicMock()
        publish_response.status_code = 200
        publish_response.json.return_value = {"id": "media_sched_001"}

        mock_post.side_effect = [container_response, publish_response]

        response = service.execute_job(job_id)

        assert response.success is True
        assert response.publishing_status == "Success"
        assert response.publication_id == "media_sched_001"

        db = SessionLocal()
        job = db.query(PublishJob).filter(PublishJob.job_id == job_id).first()
        assert job.status == PublishStatus.PUBLISHED.value
        db.close()


# ─────────────────────────────────────────────────────────────────────────────
# Unsupported Platform Test
# ─────────────────────────────────────────────────────────────────────────────

def test_unsupported_platform_returns_validation_error():
    """Test that an unsupported platform returns a clean validation error."""
    service = AutoPublishingService()
    request = PublishRequest(
        platform="TikTok",
        scheduled_datetime="2026-07-14T12:00:00",
        content="TikTok post content"
    )

    response = service.publish_post(request)

    assert response.publishing_status == "Failed"
    assert "not supported" in response.message.lower() or "validation" in response.message.lower()


def test_unsupported_platform_execute_job_returns_error():
    """Test that execute_job with an unsupported platform returns a failure."""
    service = AutoPublishingService()
    request = PublishRequest(
        platform="TikTok",
        scheduled_datetime="2026-07-14T12:00:00",
        content="TikTok job content"
    )

    schedule_res = service.schedule_post(request)
    job_id = schedule_res.job["job_id"]
    approve_job_in_db(job_id)

    response = service.execute_job(job_id)

    assert response.success is False
    assert "Unsupported platform" in response.message or "not supported" in response.message.lower()


# ─────────────────────────────────────────────────────────────────────────────
# Rate Limiting Test (HTTP 429)
# ─────────────────────────────────────────────────────────────────────────────

def test_rate_limit_returns_429():
    """Test that exceeding the rate limit on /chat returns HTTP 429."""
    client = TestClient(app, raise_server_exceptions=False)

    # Patch the router to respond instantly without making real LLM calls
    mock_response = "Mocked AI response for rate limiting test."

    with patch("router.AIIntentRouter.process_request_async", return_value=mock_response):
        responses = []
        for _ in range(25):  # Well above the 20/minute limit
            resp = client.post("/chat", json={"message": "Hello!", "user_id": "test-rate-limit"})
            responses.append(resp.status_code)

    # At least one request should have been rate-limited (HTTP 429)
    assert 429 in responses, f"Expected a 429 response among: {set(responses)}"


# ─────────────────────────────────────────────────────────────────────────────
# publish_to_instagram_tool Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_publish_to_instagram_tool_success(mock_instagram_settings):
    """Test publish_to_instagram_tool returns success response structure when the service succeeds."""
    from tools.publishing_tool import publish_to_instagram_tool, InstagramPublishRequest

    request = InstagramPublishRequest(
        content="Testing tool call!",
        media_url="https://example.com/test.jpg"
    )

    with patch("services.instagram_service.requests.post") as mock_post:
        # Mock Step 1: create media container
        container_response = MagicMock()
        container_response.status_code = 200
        container_response.json.return_value = {"id": "container_abc123"}

        # Mock Step 2: publish media container
        publish_response = MagicMock()
        publish_response.status_code = 200
        publish_response.json.return_value = {"id": "media_xyz789"}

        mock_post.side_effect = [container_response, publish_response]

        res = publish_to_instagram_tool(request)
        assert res["success"] is True
        assert res["publication_id"] == "media_xyz789"
        assert "Successfully published" in res["message"]


# ─────────────────────────────────────────────────────────────────────────────
# New Human Approval Workflow Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_pending_review_blocks_publishing():
    """Verify that a job with status 'pending_review' blocks publishing."""
    service = AutoPublishingService()
    request = PublishRequest(
        platform="LinkedIn",
        scheduled_datetime="2026-07-14T12:00:00",
        content="Approval block test content"
    )
    schedule_res = service.schedule_post(request)
    job_id = schedule_res.job["job_id"]

    # Verify initial status is pending_review
    assert schedule_res.job["status"] == "pending_review"

    # Attempt to execute without approval
    exec_res = service.execute_job(job_id)
    assert exec_res.success is False
    assert "waiting for human approval" in exec_res.message.lower()


def test_approve_allows_publishing(mock_settings):
    """Verify that approving a job updates its status and allows execute_job to run."""
    service = AutoPublishingService()
    request = PublishRequest(
        platform="LinkedIn",
        scheduled_datetime="2026-07-14T12:00:00",
        content="Approve test content"
    )
    schedule_res = service.schedule_post(request)
    job_id = schedule_res.job["job_id"]

    client = TestClient(app)
    # Call the API endpoint to approve
    resp = client.post(f"/review/{job_id}", json={"action": "approve", "reviewer": "Alice"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["job"]["status"] == "approved"
    assert data["job"]["reviewer"] == "Alice"
    assert data["job"]["review_action"] == "approve"
    assert data["job"]["reviewed_at"] is not None

    # Now execute
    with patch("requests.get") as mock_get, patch("requests.post") as mock_post:
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {"id": "test_member_id"}
        mock_get.return_value = mock_get_response

        mock_post_response = MagicMock()
        mock_post_response.status_code = 201
        mock_post_response.json.return_value = {"id": "urn:li:share:approved_12345"}
        mock_post.return_value = mock_post_response

        exec_res = service.execute_job(job_id)
        assert exec_res.success is True
        assert exec_res.publishing_status == "Success"


def test_reject_blocks_publishing():
    """Verify that rejecting a job updates status and prevents publishing."""
    service = AutoPublishingService()
    request = PublishRequest(
        platform="LinkedIn",
        scheduled_datetime="2026-07-14T12:00:00",
        content="Reject test content"
    )
    schedule_res = service.schedule_post(request)
    job_id = schedule_res.job["job_id"]

    client = TestClient(app)
    # Reject the job
    resp = client.post(f"/review/{job_id}", json={"action": "reject", "reviewer": "Bob"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["job"]["status"] == "rejected"

    # Attempt to execute
    exec_res = service.execute_job(job_id)
    assert exec_res.success is False
    assert "waiting for human approval" in exec_res.message.lower()


def test_edit_updates_content_before_publishing(mock_settings):
    """Verify that editing a job replaces content, sets status to approved, and publishes edited text."""
    service = AutoPublishingService()
    request = PublishRequest(
        platform="LinkedIn",
        scheduled_datetime="2026-07-14T12:00:00",
        content="Original content"
    )
    schedule_res = service.schedule_post(request)
    job_id = schedule_res.job["job_id"]

    client = TestClient(app)
    # Edit the content and approve
    resp = client.post(
        f"/review/{job_id}",
        json={"action": "edit", "content": "Edited content by human", "reviewer": "Charlie"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["job"]["status"] == "approved"
    assert data["job"]["content"] == "Edited content by human"

    # Execute
    with patch("requests.get") as mock_get, patch("services.linkedin_service.LinkedInService.publish_text_post") as mock_publish:
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {"id": "test_member_id"}
        mock_get.return_value = mock_get_response

        mock_publish.return_value = "urn:li:share:edited_12345"

        exec_res = service.execute_job(job_id)
        assert exec_res.success is True
        mock_publish.assert_called_once_with("Edited content by human")


def test_invalid_review_action():
    """Verify that reviewing with an invalid action returns a validation error."""
    service = AutoPublishingService()
    request = PublishRequest(
        platform="LinkedIn",
        scheduled_datetime="2026-07-14T12:00:00",
        content="Invalid action test"
    )
    schedule_res = service.schedule_post(request)
    job_id = schedule_res.job["job_id"]

    client = TestClient(app)
    resp = client.post(f"/review/{job_id}", json={"action": "invalid_action"})
    assert resp.status_code == 400
    assert "Invalid review action" in resp.json()["detail"]


def test_reviewing_published_job_returns_validation_error(mock_settings):
    """Verify that reviewing an already-published job returns a validation error."""
    service = AutoPublishingService()
    request = PublishRequest(
        platform="LinkedIn",
        scheduled_datetime="2026-07-14T12:00:00",
        content="Published review test"
    )
    schedule_res = service.schedule_post(request)
    job_id = schedule_res.job["job_id"]
    approve_job_in_db(job_id)

    # Publish the job
    with patch("requests.get") as mock_get, patch("requests.post") as mock_post:
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {"id": "test_member_id"}
        mock_get.return_value = mock_get_response

        mock_post_response = MagicMock()
        mock_post_response.status_code = 201
        mock_post_response.json.return_value = {"id": "urn:li:share:published_12345"}
        mock_post.return_value = mock_post_response

        exec_res = service.execute_job(job_id)
        assert exec_res.success is True

    # Now attempt to review it again
    client = TestClient(app)
    resp = client.post(f"/review/{job_id}", json={"action": "approve"})
    assert resp.status_code == 400
    assert "Already published posts cannot be reviewed again" in resp.json()["detail"]
