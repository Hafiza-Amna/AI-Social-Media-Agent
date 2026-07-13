# Import all tools from the central tools package
from tools.content_generator_tool import content_generator_tool
from tools.calendar_tool import calendar_tool
from tools.scheduling_tool import scheduling_tool
from tools.publishing_tool import publishing_tool, linkedin_publish_tool
from tools.comment_tool import comment_tool
from tools.dm_tool import dm_tool
from tools.analytics_tool import analytics_tool
from tools.competitor_tool import competitor_tool
from tools.repurpose_tool import repurpose_tool
from tools.team_tool import team_tool

MASTER_AGENT_SYSTEM_PROMPT = """
You are the Master AI Agent for a production-grade Social Media Management Platform.
You operate as the central intelligence hub and orchestrator, mimicking the capabilities of an elite, world-class social media marketing agency.

Your core responsibilities encompass orchestrating and delegating tasks across the following domains:
1. Content Generation: Crafting highly engaging, platform-specific content.
2. Content Calendar: Planning cohesive, strategic, multi-day content campaigns.
3. Smart Scheduling: Analyzing historical audience data to mathematically determine the best posting times.
4. Auto Publishing: Managing the publishing queue and ensuring seamless content delivery.
5. Comment Assistant: Analyzing sentiment and generating rapid, brand-aligned replies to public comments.
6. DM Assistant: Managing direct messages, classifying user intent, and escalating complex queries.
7. Analytics: Providing deep-dive performance analysis, scoring, and predictive strategic insights.
8. Competitor Analysis: Identifying market gaps, performing SWOT analysis, and strategizing market capture.
9. Content Repurposing: Adapting core messages seamlessly across diverse social networks.
10. Team Collaboration: Overseeing task assignments, review workflows, and human-in-the-loop approval processes.

You must always maintain a professional, deeply analytical, and highly strategic tone. 
Your ultimate goal is to maximize brand growth, streamline team operations, and drive unmatched audience engagement.
"""

class MasterAgent:
    """
    LiteLLM-compatible wrapper representing the Master Agent and its tools.
    """
    def __init__(self, name: str, description: str, system_prompt: str, tools: list):
        self.name = name
        self.description = description
        self.system_prompt = system_prompt
        self.tools = tools

def create_master_agent() -> MasterAgent:
    """
    Initializes and returns the Master Social Media Agent configuration.
    """
    tools = [
        content_generator_tool,
        calendar_tool,
        scheduling_tool,
        publishing_tool,
        linkedin_publish_tool,
        comment_tool,
        dm_tool,
        analytics_tool,
        competitor_tool,
        repurpose_tool,
        team_tool,
    ]
    return MasterAgent(
        name="social_media_master_agent",
        description="The Master AI Agent for Social Media Platform.",
        system_prompt=MASTER_AGENT_SYSTEM_PROMPT,
        tools=tools,
    )

if __name__ == "__main__":
    agent = create_master_agent()
    print(agent.name)