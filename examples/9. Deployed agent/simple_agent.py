from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.os import AgentOS

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)

assistant = Agent(
    name="Assistant",
    model=OpenAIChat(id="gpt-5-mini"),
    instructions=["You are a helpful AI assistant."],
    markdown=True,
)

agent_os = AgentOS(
    os_id="DevOS",
    description="My first AgentOS",
    agents=[assistant],
)

app = agent_os.get_app()

if __name__ == "__main__":
    # Default port is 7777; change with port=...
    agent_os.serve(app="simple_agent:app", reload=True)