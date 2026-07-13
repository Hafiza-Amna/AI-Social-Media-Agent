from typing import List, Optional
from datetime import datetime
from models.social_account import SocialAccount
from models.platform_type import PlatformType
from models.account_connection import AccountConnectionRequest

class SocialAccountService:
    """
    Service responsible for managing social media account integrations, 
    connection states, and platform-specific configurations.
    """
    def __init__(self):
        # In a production application, this would be a real database session/repository.
        # We use an in-memory dictionary here as a functional placeholder for DB operations.
        self._accounts = {}

    def connect_account(self, request: AccountConnectionRequest) -> SocialAccount:
        """
        Registers and connects a new social media account.
        """
        # Create a new SocialAccount with placeholder tokens for now
        new_account = SocialAccount(
            account_id=request.account_id,
            account_name=request.account_name,
            platform=request.platform,
            access_token_placeholder="dummy_access_token_xyz_123",
            refresh_token_placeholder="dummy_refresh_token_xyz_456",
            is_connected=True,
            is_enabled=True,
            is_default=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Save to our "database"
        self._accounts[new_account.account_id] = new_account
        return new_account

    def disconnect_account(self, account_id: str) -> bool:
        """
        Marks a social media account as disconnected (invalidates tokens functionally).
        """
        if account_id in self._accounts:
            self._accounts[account_id].is_connected = False
            self._accounts[account_id].updated_at = datetime.utcnow()
            return True
        return False

    def toggle_account_status(self, account_id: str, is_enabled: bool) -> bool:
        """
        Enables or disables a connected account for active posting without disconnecting it.
        """
        if account_id in self._accounts:
            self._accounts[account_id].is_enabled = is_enabled
            self._accounts[account_id].updated_at = datetime.utcnow()
            return True
        return False

    def set_default_account(self, account_id: str) -> bool:
        """
        Marks an account as the default for its respective platform.
        Ensures only one account per platform is marked as default.
        """
        if account_id not in self._accounts:
            return False
            
        target_account = self._accounts[account_id]
        platform = target_account.platform
        
        # Unset default for all other accounts on this platform
        for acc in self._accounts.values():
            if acc.platform == platform:
                acc.is_default = False
                acc.updated_at = datetime.utcnow()
                
        # Set target as default
        target_account.is_default = True
        target_account.updated_at = datetime.utcnow()
        return True

    def get_accounts_by_platform(self, platform: PlatformType) -> List[SocialAccount]:
        """
        Retrieves all connected accounts for a specific platform.
        """
        return [acc for acc in self._accounts.values() if acc.platform == platform]
