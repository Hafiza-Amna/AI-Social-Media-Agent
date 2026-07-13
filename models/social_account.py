from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from models.platform_type import PlatformType

class SocialAccount(BaseModel):
    """
    Model representing a connected social media account with metadata and tokens.
    """
    account_id: str = Field(..., description="Unique identifier for the account on the platform.")
    account_name: str = Field(..., description="Display name or handle of the account.")
    platform: PlatformType = Field(..., description="The platform this account belongs to.")
    
    access_token_placeholder: str = Field(..., description="Placeholder for the OAuth access token.")
    refresh_token_placeholder: Optional[str] = Field(None, description="Placeholder for the OAuth refresh token.")
    
    is_connected: bool = Field(default=False, description="Whether the account is currently authenticated and connected.")
    is_enabled: bool = Field(default=True, description="Whether the account is active/enabled for posting use.")
    is_default: bool = Field(default=False, description="Whether this is the primary default account for its platform.")
    
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When the account was first connected.")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="When the account was last updated.")
