"""
models/team_request_internal.py

Internal Pydantic models for team collaboration business logic.
These are NOT used in tool schemas (which are flattened for Groq compatibility)
but are used by the TeamCollaborationService for type-safe operations.
"""
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional


class UserRole(str, Enum):
    """Enum representing the distinct roles within the collaborative team."""
    ADMIN = "Admin"
    MANAGER = "Manager"
    CONTENT_CREATOR = "Content Creator"
    REVIEWER = "Reviewer"


class TaskStatus(str, Enum):
    """Enum representing the lifecycle status of a content task."""
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    IN_REVIEW = "In Review"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    COMPLETED = "Completed"


class AssignTaskRequest(BaseModel):
    """
    Model representing a request from a Manager/Admin to assign a new content task.
    """
    title: str = Field(..., description="The title of the content task.")
    description: str = Field(..., description="Detailed instructions and requirements for the task.")
    assigned_to_user_id: str = Field(..., description="The ID of the user responsible for completing the task.")
    created_by_user_id: str = Field(..., description="The ID of the user creating the assignment.")


class UpdateTaskStatusRequest(BaseModel):
    """
    Model representing a request to update the status of an existing task.
    """
    task_id: str = Field(..., description="The unique ID of the task to update.")
    new_status: TaskStatus = Field(..., description="The new status to apply to the task.")
    user_id: str = Field(..., description="The ID of the user performing the update (e.g., the Reviewer).")
    feedback_comment: Optional[str] = Field(None, description="Optional contextual feedback.")
