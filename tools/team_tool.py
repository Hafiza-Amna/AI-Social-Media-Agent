"""
tools/team_tool.py

Tool wrapper for Team Collaboration operations.
Handles the flattened TeamRequest (action as str, payloads as dicts).
"""
import logging
from utils.tool_wrapper import FunctionTool
from models.team_request import TeamRequest
from models.team_response import TeamResponse
from services.team_collaboration_service import TeamCollaborationService

logger = logging.getLogger(__name__)
_team_service = TeamCollaborationService()


def manage_team(request: TeamRequest) -> TeamResponse:
    """
    Manages team collaboration: assigns content tasks, updates task statuses, and retrieves dashboard metrics.
    Provide a TeamRequest with the action (Assign Task, Update Status, Get Dashboard) and its payload.
    """
    logger.info(f"Executing 'manage_team' with action: '{request.action}'.")

    try:
        action_lower = request.action.strip().lower()

        if action_lower == "assign task":
            if not request.assign_task_payload:
                raise ValueError("Validation Error: assign_task_payload must be provided for Assign Task.")
            # Convert dict payload to the Pydantic model the service expects
            from models.team_request_internal import AssignTaskRequest
            payload = AssignTaskRequest(**request.assign_task_payload)
            task = _team_service.assign_task(payload)
            logger.info(f"Task '{task.task_id}' assigned successfully.")
            return TeamResponse(success=True, message=f"Task '{task.title}' assigned to {task.assigned_to}.", task=task)

        elif action_lower == "update status":
            if not request.update_status_payload:
                raise ValueError("Validation Error: update_status_payload must be provided for Update Status.")
            from models.team_request_internal import UpdateTaskStatusRequest
            payload = UpdateTaskStatusRequest(**request.update_status_payload)
            task = _team_service.update_task_status(payload)
            logger.info(f"Task '{task.task_id}' status updated to '{task.status}'.")
            return TeamResponse(success=True, message=f"Task status updated to {task.status}.", task=task)

        elif action_lower == "get dashboard":
            dashboard = _team_service.get_dashboard_summary()
            logger.info("Team dashboard summary retrieved successfully.")
            return TeamResponse(success=True, message="Dashboard summary retrieved.", dashboard_summary=dashboard)

        else:
            raise ValueError(f"Unknown action: '{request.action}'. Allowed: Assign Task, Update Status, Get Dashboard")

    except ValueError as ve:
        logger.warning(f"Bad Request in manage_team: {ve}")
        return TeamResponse(success=False, message=str(ve))
    except Exception as e:
        logger.error(f"Unexpected execution error in manage_team: {e}", exc_info=True)
        raise RuntimeError(f"Tool Execution Failed: Unable to perform team collaboration action -> {str(e)}")


team_tool = FunctionTool(func=manage_team)
