from typing import Optional
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from models.team_request_internal import UserRole, TaskStatus

class TeamMember(BaseModel):
    """Model representing a user in the system."""
    user_id: str = Field(..., description="Unique user identifier.")
    name: str = Field(..., description="Display name of the user.")
    role: UserRole = Field(..., description="The user's role and permission level.")

class ContentTask(BaseModel):
    """
    Model representing a content creation task, including its full audit trail and feedback.
    """
    task_id: str = Field(...)
    title: str = Field(...)
    description: str = Field(...)
    assigned_to: str = Field(...)
    created_by: str = Field(...)
    status: TaskStatus = Field(...)
    feedback: List[str] = Field(default_factory=list, description="A chronological list of feedback comments left by reviewers.")
    activity_history: List[str] = Field(default_factory=list, description="An audit trail of all status changes and updates.")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class DashboardSummaryResponse(BaseModel):
    """
    Model representing a high-level overview of the team's operational status.
    """
    total_members: int = Field(..., description="Total number of active team members.")
    pending_tasks: List[ContentTask] = Field(..., description="Tasks currently pending or actively being worked on.")
    completed_tasks: List[ContentTask] = Field(..., description="Tasks that are fully finished.")
    tasks_in_review: List[ContentTask] = Field(..., description="Tasks actively undergoing the approval or rejection process.")
    recent_activity: List[str] = Field(..., description="A global audit log of recent team activity.")

class TeamResponse(BaseModel):
    """
    Unified model representing the response from the Team Collaboration module.
    """
    success: bool = Field(..., description="True if the operation was successful.")
    message: str = Field(..., description="A human-readable success or error message.")
    task: Optional[ContentTask] = Field(None, description="The created or updated task, if applicable.")
    dashboard_summary: Optional[DashboardSummaryResponse] = Field(None, description="The dashboard summary, if requested.")
