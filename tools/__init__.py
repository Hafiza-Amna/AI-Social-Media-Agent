"""
Google ADK Tools Package

This package serves as the central registry and export hub for all custom tools 
available to the Master AI Agent (social_media_master_agent). 

By structuring the tools within this package, we adhere strictly to clean architecture principles:
1. Encapsulation: Each tool implementation resides in its own isolated module.
2. Centralized Exports: This __init__.py file aggregates all tools, allowing the master 
   agent to import them seamlessly from a single source without worrying about internal routing.
"""

from .content_generator_tool import content_generator_tool
from .calendar_tool import calendar_tool
from .scheduling_tool import scheduling_tool
from .publishing_tool import publishing_tool
from .comment_tool import comment_tool
from .dm_tool import dm_tool
from .analytics_tool import analytics_tool
from .competitor_tool import competitor_tool
from .repurpose_tool import repurpose_tool
from .team_tool import team_tool

# ==============================================================================
# Package Exports
# Defines the public interface of the tools package for the Master Agent.
# ==============================================================================
__all__ = [
    "content_generator_tool",
    "calendar_tool",
    "scheduling_tool",
    "publishing_tool",
    "comment_tool",
    "dm_tool",
    "analytics_tool",
    "competitor_tool",
    "repurpose_tool",
    "team_tool"
]
