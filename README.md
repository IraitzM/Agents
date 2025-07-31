# Agents

Examples on how to build agents and different patterns to be used.

## Frameworks

We will explore how agents can be implemented using different technologies:

* [LangChain](https://www.langchain.com/)
* [Agno](https://github.com/agno-agi/agno)

## Tools & resources

In order to perform actions programmatically we will be using a set of tools and resources.

* [Tavily](https://www.tavily.com/) for online search (or [Serper](https://serper.dev/))
* [LangSmith](https://smith.langchain.com/) for agent action tracing
* [LanceDB](lancedb.com) and [FAISS](https://faiss.ai/) for embedding storage and retrieval

## Credentials

Make sure you have some Gemini credentials ready to test the examples. Take _.env.example_ file to create your own _.env_ file. Some extra bits on self-hosted infra are shown but this may require performant hardware on you end so we will show most of the exercises based on Gemini subscriptions.

## Environment

You can either use `pip` to add dependencies using the `requirements.txt` file or simply call `uv sync`.
