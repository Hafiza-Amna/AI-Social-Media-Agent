"""
services/instagram_service.py

Handles real API interactions with the Instagram Graph API using the Access Token and Business Account ID.
"""
import logging
import requests
from config import settings

logger = logging.getLogger(__name__)

class InstagramService:
    """
    Service to interact with the Instagram Graph API for publishing posts.
    """

    def __init__(self) -> None:
        self.access_token = settings.IG_ACCESS_TOKEN
        self.business_account_id = settings.IG_BUSINESS_ACCOUNT_ID
        self.base_url = "https://graph.facebook.com/v17.0"

    def create_media_container(self, caption: str, media_url: str) -> str:
        """
        Step 1: Create a media container on Instagram.
        Returns the container ID (creation ID) on success.
        """
        if not self.access_token:
            raise ValueError(
                "Instagram Access Token is missing. Please add IG_ACCESS_TOKEN to your .env file."
            )
        if not self.business_account_id:
            raise ValueError(
                "Instagram Business Account ID is missing. Please add IG_BUSINESS_ACCOUNT_ID to your .env file."
            )
        if not media_url:
            raise ValueError("Instagram requires a media URL (image or video) to publish.")

        url = f"{self.base_url}/{self.business_account_id}/media"
        # Basic check to determine if video or image
        is_video = any(media_url.lower().endswith(ext) for ext in [".mp4", ".mov", ".m4v"])
        
        payload = {
            "caption": caption,
            "access_token": self.access_token
        }
        if is_video:
            payload["media_type"] = "VIDEO"
            payload["video_url"] = media_url
        else:
            payload["image_url"] = media_url

        logger.info(f"[Instagram] Creating media container for {'video' if is_video else 'image'} | url={url}")
        try:
            response = requests.post(url, data=payload)
        except Exception as e:
            raise RuntimeError(f"Failed to connect to Instagram Graph API: {e}")

        if response.status_code not in (200, 201):
            logger.error(f"[Instagram] Failed to create container: {response.status_code} - {response.text}")
            self._handle_api_errors(response)

        data = response.json()
        container_id = data.get("id")
        if not container_id:
            raise RuntimeError("Instagram response did not contain a container 'id'.")
        return container_id

    def publish_media_container(self, creation_id: str) -> str:
        """
        Step 2: Publish the media container.
        Returns the published media ID on success.
        """
        url = f"{self.base_url}/{self.business_account_id}/media_publish"
        payload = {
            "creation_id": creation_id,
            "access_token": self.access_token
        }

        logger.info(f"[Instagram] Publishing media container {creation_id} | url={url}")
        try:
            response = requests.post(url, data=payload)
        except Exception as e:
            raise RuntimeError(f"Failed to connect to Instagram Graph API: {e}")

        if response.status_code not in (200, 201):
            logger.error(f"[Instagram] Failed to publish container: {response.status_code} - {response.text}")
            self._handle_api_errors(response)

        data = response.json()
        media_id = data.get("id")
        if not media_id:
            raise RuntimeError("Instagram response did not contain a published media 'id'.")
        return media_id

    def _handle_api_errors(self, response: requests.Response) -> None:
        """
        Parses response errors and raises appropriate RuntimeError exceptions.
        """
        try:
            error_data = response.json().get("error", {})
            error_msg = error_data.get("message", response.text)
            error_code = error_data.get("code")
        except Exception:
            error_msg = response.text
            error_code = None

        if response.status_code == 401 or error_code in (190, 102):
            raise RuntimeError("Instagram token is invalid or expired. Please check your IG_ACCESS_TOKEN.")
        elif response.status_code == 403 or error_code in (10, 200, 341):
            raise RuntimeError("Instagram permission denied. Ensure necessary permissions (instagram_basic, instagram_content_publish) are granted.")
        
        raise RuntimeError(
            f"Instagram Publishing API Error ({response.status_code}): {error_msg}"
        )

    def publish_instagram_post(self, content: str, media_url: str) -> str:
        """
        Publishes a post to Instagram on behalf of the business account.
        Returns the publication ID (media ID) on success.
        """
        logger.info(f"[Instagram] Initiating publishing flow. Content length: {len(content)} chars")
        container_id = self.create_media_container(content, media_url)
        media_id = self.publish_media_container(container_id)
        return media_id


def publish_to_instagram(content: str, media_url: str = None) -> dict:
    """
    Exposes a clean standalone function to publish content to Instagram.
    Returns a success/failure dictionary.
    """
    try:
        service = InstagramService()
        media_id = service.publish_instagram_post(content, media_url)
        return {
            "success": True,
            "publication_id": media_id,
            "message": "Successfully published post to Instagram."
        }
    except Exception as e:
        logger.error(f"publish_to_instagram failed: {e}", exc_info=True)
        return {
            "success": False,
            "publication_id": None,
            "message": f"Failed to publish to Instagram: {str(e)}"
        }
