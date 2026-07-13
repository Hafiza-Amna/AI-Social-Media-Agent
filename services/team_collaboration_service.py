import uuid
from datetime import datetime
from typing import List, Dict
from models.team_request_internal import UserRole, TaskStatus, AssignTaskRequest, UpdateTaskStatusRequest
from models.team_response import TeamMember, ContentTask, DashboardSummaryResponse

class TeamCollaborationService:
    """
    Service responsible for managing team members, orchestrating task assignments, 
    tracking content approvals/rejections, and providing real-time dashboard summaries.
    """
    def __init__(self):
        # We use in-memory dictionaries here as a robust functional placeholder 
        # until the real SQL database layer is implemented.
        self._members: Dict[str, TeamMember] = {
            "u1": TeamMember(user_id="u1", name="Alice", role=UserRole.ADMIN),
            "u2": TeamMember(user_id="u2", name="Bob", role=UserRole.MANAGER),
            "u3": TeamMember(user_id="u3", name="Charlie", role=UserRole.CONTENT_CREATOR),
            "u4": TeamMember(user_id="u4", name="Diana", role=UserRole.REVIEWER),
        }
        self._tasks: Dict[str, ContentTask] = {}
        self._global_activity: List[str] = []

    def _log_activity(self, message: str, task: ContentTask = None):
        """Helper method to ensure every action is securely audited both globally and at the task level."""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        self._global_activity.insert(0, log_msg)
        if task:
            task.activity_history.insert(0, log_msg)
            task.updated_at = datetime.utcnow()

    def assign_task(self, request: AssignTaskRequest) -> ContentTask:
        """
        Creates and assigns a new content task to a specific team member.
        """
        if request.assigned_to_user_id not in self._members:
            raise ValueError(f"Assignee user ID {request.assigned_to_user_id} not found.")
        if request.created_by_user_id not in self._members:
            raise ValueError(f"Creator user ID {request.created_by_user_id} not found.")

        task_id = str(uuid.uuid4())
        new_task = ContentTask(
            task_id=task_id,
            title=request.title,
            description=request.description,
            assigned_to=request.assigned_to_user_id,
            created_by=request.created_by_user_id,
            status=TaskStatus.PENDING
        )
        self._tasks[task_id] = new_task
        
        creator_name = self._members[request.created_by_user_id].name
        assignee_name = self._members[request.assigned_to_user_id].name
        self._log_activity(f"New task '{new_task.title}' assigned to {assignee_name} by {creator_name}.", new_task)
        
        return new_task

    def update_task_status(self, request: UpdateTaskStatusRequest) -> ContentTask:
        """
        Updates the status of a task (e.g., submitting for review, approving, rejecting),
        appends any feedback provided by the reviewer, and meticulously logs the activity.
        """
        if request.task_id not in self._tasks:
            raise ValueError("Task ID not found in the system.")
        if request.user_id not in self._members:
            raise ValueError("User ID performing the update not found.")
            
        task = self._tasks[request.task_id]
        user_name = self._members[request.user_id].name
        
        old_status = task.status
        task.status = request.new_status
        
        # If a reviewer provides feedback (e.g., when rejecting), append it to the task's feedback trail
        if request.feedback_comment:
            feedback_entry = f"[{user_name}]: {request.feedback_comment}"
            task.feedback.append(feedback_entry)
            
        self._log_activity(f"{user_name} transitioned task status from '{old_status.value}' to '{request.new_status.value}'.", task)
        
        return task

    def get_dashboard_summary(self) -> DashboardSummaryResponse:
        """
        Aggregates and returns a comprehensive, real-time summary of team operational metrics and tasks.
        """
        tasks = list(self._tasks.values())
        
        pending = [t for t in tasks if t.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]]
        completed = [t for t in tasks if t.status == TaskStatus.COMPLETED]
        in_review = [t for t in tasks if t.status in [TaskStatus.IN_REVIEW, TaskStatus.APPROVED, TaskStatus.REJECTED]]
        
        return DashboardSummaryResponse(
            total_members=len(self._members),
            pending_tasks=pending,
            completed_tasks=completed,
            tasks_in_review=in_review,
            recent_activity=self._global_activity[:10]  # Return the 10 most recent global activity logs
        )
