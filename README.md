# Reckonsys Gen AI Dev Assignment: Agentic RAG Challenge

**Obligatory notice**: I am solely responsible for the work in this repo and no help of Generative AI has been taken for the entirety of this project. Please see [references](references.html) for all the external resources used. 

## Introduction

Objective: Build a basic agentic RAG system where the agent autonomously decides whether to retrieve answers from documents or search the web when confidence is low.

## Tech
1. Backend: FastAPI
2. Agent: Langchain
3. MCP Server: FastMCP
4. MCP Tools:
    1. web_search: Tavily
    2. rag_search: Milvus, Mixedbread
5. Dataset generation
    1. Network calls: asyncio, requests, aiohttp, backoff
    2. Content parsing: BeautifulSoup
    3. Preprocessing: langchain_text_splitters, datasets, pandas
    4. Vectordb: Milvus

## Workflow:

- User makes a `POST` request to the `/chat` endpoint. 

- Agent calls the mcp server and uses the **tools** in **ReAct** style. 

- Tool calling directions and threshold (`0.8`) is controlled via the prompt.

- After satisfactory searches, agent responds

## How to run

0. Setup venv using uv:
```bash
uv sync
source .venv/bin/activate
```

1. Run the MCP server (port 9000) via:
```bash
uv run mcp_server/main.py 
```

2. Run the FastAPI backend (port 8000) via:
```bash
fastapi run backend/main.py
```

3. Go to `http://127.0.0.1:8000/docs` and enjoy!