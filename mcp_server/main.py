import asyncio
import os
import logging

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from tavily import AsyncTavilyClient
from pymilvus import MilvusClient
from mixedbread import AsyncMixedbread

# Reads variables from a .env file and sets them in os.environ
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("tavily_search", host="0.0.0.0", port=8000)

# Initialise Tavily client
tavily_client = AsyncTavilyClient(os.getenv("TAVILY_API_KEY"))

# Initialise Milvus Client
milvus_client = MilvusClient("dataset/data/milvus.db")

# Instantiate mixbai client
mxbai_client = AsyncMixedbread(api_key=os.getenv("MXBAI_API_KEY"))

# TODO: Make a config file for all the parameters like collection name


# TODO: Make a pydantic model to validate the results
# TODO: Add option to modify search results
# Function to make async requests to tavily search api
async def make_tavily_request(query: str) -> dict | None:
    logging.info("make_tavily_request")
    logging.info(query)

    # Perform search
    try:
        response = await tavily_client.search(query, search_depth="basic")

        logging.info(response)

        return response

    # Handle error
    except Exception as e:
        logging.error(f"Error during make_tavily_request for  query {query}")
        logging.error(f"Error : {e}")
        return None


# Function to format response
def format_web_search_results(result: dict) -> str:
    logging.info("Formatting web search results")
    logging.info(result)

    # Format results
    formatted_result = f"""
    Title: {result.get("title", "Unknown")}
    Content: {result.get("content", "Unknown")}
    URL: {result.get("url", "Unknown")}
    """

    logging.info("Formatted result:")
    logging.info(formatted_result)

    return formatted_result


# MCP tool for the agent
@mcp.tool()
async def web_search(query: str) -> str:
    """
    Tool to search the web using Tavily

    Args:
        query: The user query

     Returns:
         Formatted search results
    """

    # Perform tavily request
    search_results = await make_tavily_request(query)

    # TODO: Make agent fall back to rag results if tavily fails
    if not search_results:
        return "Unable to perform WEB search"

    # Format results to be passed to LLM
    formatted_search_results = [
        format_web_search_results(result) for result in search_results["results"]
    ]

    return "\n---\n".join(formatted_search_results)


# TODO: change print to log statements
async def make_milvus_request(query: str):
    logging.info("make_milvus_request")
    logging.info(query)

    # Embed the query
    try:
        response = await mxbai_client.embed(
            model="mixedbread-ai/mxbai-embed-large-v1",
            input=query,
            normalized=True,
            encoding_format="float",
        )

        logging.info("MXBAI embed response")
        # logging.info(response.)

        embedding = response.data[0].embedding

    except Exception as e:
        logging.error("Could not create embeddings via MXBAI")
        logging.error(f"Error: {e}")
        return None

    # Run similarity search via milvus
    try:
        results = milvus_client.search(
            collection_name="reckonsys",
            data=[embedding],
            limit=5,
            output_fields=["source", "page_content", "id"],
        )

        logging.info("milvus search response")
        logging.info(results)

    except Exception as e:
        logging.error("Could not search query via Milvus")
        logging.error(f"Error: {e}")
        return None

    return results


# Format rag search results
def format_rag_search_result(result: dict) -> str:
    logging.info("format_rag_search_result")

    # Get the results entity which contains data for the similarity search
    entity = result.get("entity", None)

    if entity:
        logging.info(entity)

        # Format for LLM
        formatted_result = f"""
        Text: {entity.get("page_content", "Unknown")}
        Source: {entity.get("source", "Unknown")}
        """
    else:
        logging.error("Entity not found in milvus results")

        # Fallback text
        formatted_result = """
        Text: Unknown
        Source: Unknown
        """

    logging.info(formatted_result)

    return formatted_result


# Tool to search vectordb
@mcp.tool()
async def rag_search(query: str) -> str:
    """
    Tool to search the RAG using Milvus

    Args:
        query: The user query

     Returns:
         Formatted search results
    """

    # Fetch similar results
    search_results = await make_milvus_request(query)

    # Fallback text
    if not search_results:
        return "Unable to perform RAG search"

    # Format results for LLM
    formatted_search_results = [
        format_rag_search_result(result) for result in search_results[0]
    ]

    return "\n---\n".join(formatted_search_results)


def main():
    # Initialize and run the server
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
