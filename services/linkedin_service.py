"""
services/linkedin_service.py

Handles real API interactions with the LinkedIn API using the User Access Token.
"""
import logging
import requests
from config import settings

logger = logging.getLogger(__name__)

class LinkedInService:
    """
    Service to interact with the LinkedIn REST API for publishing posts.
    """

    def __init__(self) -> None:
        self.access_token = settings.LINKEDIN_ACCESS_TOKEN
        self.base_url = "https://api.linkedin.com"

    def get_member_urn(self) -> str:
        """
        Retrieves the authenticated member's URN (urn:li:person:ID) using the access token.
        """
        if not self.access_token:
            raise ValueError(
                "LinkedIn Access Token is missing. Please add LINKEDIN_ACCESS_TOKEN to your .env file."
            )

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Connection": "Keep-Alive",
        }
        
        person_id = None
        
        # We call the /v2/me endpoint first
        url = f"{self.base_url}/v2/me"
        logger.info("Fetching LinkedIn profile data from /v2/me...")
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                person_id = data.get("id")
            else:
                logger.warning(f"Profile API /v2/me returned status {response.status_code}: {response.text}")
        except Exception as e:
            logger.warning(f"Failed to connect to /v2/me: {e}")

        # Fallback to /v2/userinfo (Sign In with LinkedIn OIDC endpoint)
        if not person_id:
            logger.info("Trying OIDC /v2/userinfo endpoint...")
            url_userinfo = f"{self.base_url}/v2/userinfo"
            try:
                response_userinfo = requests.get(url_userinfo, headers=headers)
                if response_userinfo.status_code == 200:
                    data_ui = response_userinfo.json()
                    person_id = data_ui.get("sub")
                else:
                    logger.error(f"Userinfo API returned status {response_userinfo.status_code}: {response_userinfo.text}")
            except Exception as e:
                logger.error(f"Failed to connect to /v2/userinfo: {e}")

        if not person_id:
            raise RuntimeError(
                "Could not retrieve LinkedIn member ID from either /v2/me or /v2/userinfo. Please check your credentials/scopes."
            )
            
        return f"urn:li:person:{person_id}"


    def publish_text_post(self, content: str) -> str:
        """
        Publishes a text post to LinkedIn on behalf of the member.
        Returns the publication URN (ID) on success.
        """
        author_urn = self.get_member_urn()
        logger.info(f"Resolved LinkedIn Author URN: {author_urn}")

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json",
        }

        url = f"{self.base_url}/v2/ugcPosts"
        payload = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        logger.info("Sending post request to LinkedIn /v2/ugcPosts...")
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code not in (200, 201):
            logger.error(f"Failed to publish to LinkedIn: {response.status_code} - {response.text}")
            raise RuntimeError(
                f"LinkedIn Publishing API Error ({response.status_code}): {response.text}"
            )

        data = response.json()
        # UGC posts endpoint returns URN in the 'id' field of the response payload
        ugc_urn = data.get("id")
        if not ugc_urn:
            logger.warning("LinkedIn response did not contain an 'id' field, returning default URN.")
            return f"urn:li:share:unknown_{response.status_code}"
            
        return ugc_urn

    @staticmethod
    def update_env_token(token: str) -> None:
        """
        Updates the LINKEDIN_ACCESS_TOKEN in memory settings and in the .env file.
        """
        # Update setting in memory
        settings.LINKEDIN_ACCESS_TOKEN = token
        
        # Write to .env file
        import os
        env_path = ".env"
        if not os.path.exists(env_path):
            logger.warning(f".env file not found at {env_path}, creating a new one.")
            with open(env_path, "w", encoding="utf-8") as f:
                f.write(f'LINKEDIN_ACCESS_TOKEN="{token}"\n')
            return

        try:
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            updated = False
            new_lines = []
            for line in lines:
                if line.strip().startswith("LINKEDIN_ACCESS_TOKEN="):
                    new_lines.append(f'LINKEDIN_ACCESS_TOKEN="{token}"\n')
                    updated = True
                else:
                    new_lines.append(line)
            
            if not updated:
                new_lines.append(f'\nLINKEDIN_ACCESS_TOKEN="{token}"\n')
                
            with open(env_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            
            logger.info("Successfully updated LINKEDIN_ACCESS_TOKEN in .env file.")
        except Exception as e:
            logger.error(f"Failed to update LINKEDIN_ACCESS_TOKEN in .env: {e}")


def publish_to_linkedin(content: str) -> dict:
    """
    Exposes a clean standalone function to publish content to LinkedIn using the stored token.
    Returns a success/failure dictionary.
    """
    try:
        service = LinkedInService()
        urn = service.publish_text_post(content)
        return {
            "success": True,
            "publication_id": urn,
            "message": "Successfully published post to LinkedIn."
        }
    except Exception as e:
        logger.error(f"publish_to_linkedin failed: {e}", exc_info=True)
        return {
            "success": False,
            "publication_id": None,
            "message": f"Failed to publish to LinkedIn: {str(e)}"
        }


