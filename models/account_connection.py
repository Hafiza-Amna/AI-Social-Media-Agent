from pydantic import BaseModel, Field
from models.platform_type import PlatformType

class AccountConnectionRequest(BaseModel):
    """
    Model representing the basic input required to initiate an account connection.
    (This will eventually map to the final stage of an OAuth flow).
    """
    platform: PlatformType = Field(..., description="The platform to connect to.")
    account_name: str = Field(..., description="The name or handle of the account.")
    account_id: str = Field(..., description="The platform-specific ID of the account.")
