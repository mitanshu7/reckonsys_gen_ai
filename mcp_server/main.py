import os

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from tavily import AsyncTavilyClient

# Reads variables from a .env file and sets them in os.environ
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("tavily_search", host="0.0.0.0", port=8000)

# Initialise Tavily client
tavily_client = AsyncTavilyClient(os.getenv("TAVILY_API_KEY"))


# TODO: Make a pydantic model to validate the results
# TODO: Add option to modify search results
# Function to make async requests to tavily search api
async def make_tavily_request(query: str) -> dict | None:
    # Perform search
    try:
        response = await tavily_client.search(query, search_depth="basic")
        return response

    # Handle error
    except Exception as e:
        print(f"Error during search queries: {e}")
        return None


# Function to format response
def format_search_results(result: dict) -> str:
    formatted_result = f"""
    Title: {result.get("title", "Unknown")}
    Content: {result.get("content", "Unknown")}
    URL: {result.get("url", "Unknown")}
    """

    return formatted_result


# MCP tool for the agent
@mcp.tool()
async def web_search(query: str) -> str:
    """
    Search the web

    Args:
        query: The user query

     Returns:
         Formatted search results
    """

    search_results = await make_tavily_request(query)

    # TODO: Make agent fall back to rag results if tavily fails
    if not search_results:
        return "Unable to perform web search"

    formatted_search_results = [
        format_search_results(result) for result in search_results["results"]
    ]

    return "\n---\n".join(formatted_search_results)


def main():
    # Initialize and run the server
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
