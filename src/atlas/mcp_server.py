"""Lightweight MCP Server that proxies to HTTP backend

This MCP server calls the persistent HTTP RAG server instead of doing
RAG operations locally. Keep the HTTP server running globally:
    python http_server.py

Then run this MCP server in each Claude Code instance:
    python -m atlas.mcp_server
"""

import logging
import httpx

from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("rag-agent")

# HTTP server endpoint
RAG_SERVER_URL = "http://127.0.0.1:8000"
HTTP_TIMEOUT = 30.0


@mcp.tool()
def search_rag(query: str, top_k: int = 5) -> str:
    """
    Search through indexed documents using the RAG pipeline.

    Queries the persistent HTTP RAG server for relevant documents.

    Args:
        query: The search query or question to retrieve relevant documents for
        top_k: Number of top results to return (default: 5, max: 20)

    Returns:
        Formatted string with retrieved documents and metadata
    """
    try:
        # Call the HTTP backend
        with httpx.Client(timeout=HTTP_TIMEOUT) as client:
            response = client.post(
                f"{RAG_SERVER_URL}/search",
                params={"query": query, "top_k": top_k},
            )
            response.raise_for_status()
            data = response.json()

        # Format results
        results = data.get("results", [])
        if not results:
            return "No documents found."

        output = f"Retrieved {len(results)} documents:\n\n"
        for result in results:
            output += f"--- Document {result['rank']} ---\n"
            content = result["content"]
            if len(content) > 1000:
                content = content[:997].rstrip() + "..."
            output += f"{content}\n"

            if result["metadata"]:
                output += f"[Source: {result['metadata'].get('path', 'unknown')}]\n"
            output += "\n"

        return output

    except Exception as e:
        error_msg = f"Error querying RAG server: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise ValueError(error_msg) from e


def main():
    """Entry point for MCP server"""
    try:
        logger.info(f"Starting RAG MCP server (proxying to {RAG_SERVER_URL})...")
        logger.info("Make sure http_server.py is running globally")
        mcp.run()
    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
