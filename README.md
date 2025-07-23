# Agents

Examples on how to build agents and different patterns to be used.

## Frameworks

We will explore how agents can be implemented using different technologies:

* [LangChain](https://www.langchain.com/)
* [Agno](https://github.com/agno-agi/agno)
* [CrewAI](https://www.crewai.com/)
* [Pydantic AI](https://ai.pydantic.dev/)

## Tools & resources

In order to perform actions programmatically we will be using a set of tools and resources.

* [Tavily](https://www.tavily.com/) for online search
* [LangSmith](https://smith.langchain.com/) for agent action tracing
* [LanceDB](lancedb.com) for embedding storage and retrieval

## Credentials

Make sure you have some Gemini credentials ready to test the examples. Take _.env.example_ file to create your own _.env_ file.

## Environment

You can either use `pip` to add dependencies using the `requirements.txt` file or simply call `uv sync`.
