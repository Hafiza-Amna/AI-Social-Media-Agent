from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class TeamRequest(BaseModel):
    """
    Unified model representing a request to the Team Collaboration module.
    The Master Agent uses this to multiplex different team operations into a single tool.
    """
    action: str = Field(
        ...,
        description="The specific team operation to execute. Allowed values: Assign Task, Update Status, Get Dashboard"
    )
    assign_task_payload: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Required only if action is 'Assign Task'. Keys: title (str), description (str), assigned_to_user_id (str), created_by_user_id (str)."
    )
    update_status_payload: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Required only if action is 'Update Status'. Keys: task_id (str), new_status (str: Pending|In Progress|In Review|Approved|Rejected|Completed), user_id (str), feedback_comment (optional str)."
    )
