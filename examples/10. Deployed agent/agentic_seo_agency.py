"""Custom SEO Agency."""
from agno.os import AgentOS
from agno.team import Team

from agno.agent import Agent
from agno.models.google import Gemini

from agno.tools.tavily import TavilyTools
from agno.tools.reasoning import ReasoningTools

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)

# Search engine
search = TavilyTools(
    include_answer=True,
    search_depth='basic',
    format='markdown',
    max_tokens=100
)

# Agents
seo_analyst = Agent(
    name="SEO Analyst",
    role="Discovers the keywords needed to boost the position of the site to be improved.",
    model=Gemini(id="gemini-2.5-flash", temperature=0),
    tools=[search],
    instructions="""
        Backstory:
        
        You work in Spain, most of your requests come from Spanish companies so you prioritize the positioning in Spanish speaking searches.
        Your specialty is identifying keywords to better position the products highlighted by the company.
        You conduct research on competitors and search results to better differentiate the offering and be more competitive.

        Response format:
        Always include sources.
    """,
)

strategist = Agent(
    name="Content strategist",
    role="Creates attractive and engaging content to improve SEO positioning.",
    model=Gemini(id="gemini-2.5-flash", temperature=0.6),
    tools=[search], # It might not need it but just in case
    instructions="""
        Backstory:
        
        You are a renowned Content Strategist, known for your insightful and engaging articles.
        Your specialty is transforming complex concepts into captivating narratives with high SEO impact.

        Response format:
        Always include sources.
    """,
)

# Team
seo_team = Team(
    name="SEO improving content creation team",
    model=Gemini(id="gemini-2.5-flash", temperature=0.3),
    members=[seo_analyst, strategist],
    tools=[ReasoningTools(add_instructions=True)],
    instructions=[
        "Collaborate to provide comprehensive SEO improving insights",
        "Consider both keyword research and content quality",
        "Use an engaging language to provide guidance to the user asking the questions",
        "Present findings in a structured, easy-to-follow format",
        "Only output the final consolidated response, not individual agent responses",
    ],
    markdown=True,
    show_members_responses=True,
    enable_agentic_state=True,
)

# Setup our AgentOS app
agent_os = AgentOS(
    description="My custom SEO agency",
    agents=[seo_analyst, strategist],
    teams=[seo_team],
    workflows=[],
)
app = agent_os.get_app()


if __name__ == "__main__":
    """Run your AgentOS.

    You can see the configuration and available apps at:
    http://localhost:7777/config

    """
    agent_os.serve(app="agentic_seo_agency:app", reload=True)
