import os
from backend.schemas import TextRequest

from fastapi import FastAPI
from langchain_mcp_adapters.client import MultiServerMCPClient  
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv



# Reads variables from a .env file and sets them in os.environ
load_dotenv()


model = ChatOpenAI(
    model="minimax/minimax-m2:free",  # Specify a model available on OpenRouter
    api_key=os.getenv('OPENROUTER_API_KEY'),
    base_url="https://openrouter.ai/api/v1",
)

app = FastAPI()

mcp_client = MultiServerMCPClient(
    {
        "search": {
            "transport": "streamable_http",
            "url": "http://0.0.0.0:9000/mcp"
        },
    }
)

# ReAct template
# https://smith.langchain.com/hub/hwchase17/react
template = '''Answer the following questions as best you can. You have access to the following tools:

{tools}

Always use rag_search first. Only use web_search if the confidence score is less that 0.8 for the first result, initiate a web_search.

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: The final answer should be returned as a list of dictionaries/rows. The keys to be included are Title, Company, Location, Link. Example: [{{"Title":"","Company":"","Location":"","Link":""}}]

Begin!

Question: {input}
Thought:{agent_scratchpad}'''

@app.post("/chat")
async def chat(request:TextRequest):
 
    query = request.text
 
    tools = await mcp_client.get_tools()
    
    agent = create_agent(model=model, tools=tools, system_prompt=template)
    
    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": query}]}
    )
    
    return response
    
