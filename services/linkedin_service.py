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
        
        # We call the /v2/me endpoint to get the member profile id
        url = f"{self.base_url}/v2/me"
        logger.info("Fetching LinkedIn profile data from /v2/me...")
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch LinkedIn profile: {response.status_code} - {response.text}")
            raise RuntimeError(
                f"LinkedIn Profile API Error ({response.status_code}): {response.text}"
            )
            
        data = response.json()
        person_id = data.get("id")
        if not person_id:
            raise ValueError("Could not find 'id' field in LinkedIn profile response.")
            
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

