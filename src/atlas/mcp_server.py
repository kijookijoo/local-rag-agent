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


def _format_search_results(results: list, method: str) -> str:
    """Format search results for display."""
    if not results:
        return "No documents found."

    output = f"Retrieved {len(results)} documents ({method} search):\n\n"
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


@mcp.tool()
def search_keyword(query: str, top_k: int = 5) -> str:
    """
    Fast keyword search using BM25 matching.

    Best for: Specific terms, code identifiers, exact matches, quick lookups.
    Speed: Very fast (milliseconds)

    Args:
        query: The search query with specific keywords
        top_k: Number of results to return (default: 5, max: 20)

    Returns:
        Formatted string with matching documents
    """
    try:
        with httpx.Client(timeout=HTTP_TIMEOUT) as client:
            response = client.post(
                f"{RAG_SERVER_URL}/search/keyword",
                params={"query": query, "top_k": top_k},
            )
            response.raise_for_status()
            data = response.json()

        results = data.get("results", [])
        return _format_search_results(results, "keyword")

    except Exception as e:
        error_msg = f"Error in keyword search: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise ValueError(error_msg) from e


@mcp.tool()
def search_semantic(query: str, top_k: int = 5) -> str:
    """
    Semantic search using vector similarity.

    Best for: Understanding meaning, conceptual queries, paraphrased questions.
    Speed: Slower (seconds, needs embedding model)

    Args:
        query: The search query in natural language
        top_k: Number of results to return (default: 5, max: 20)

    Returns:
        Formatted string with semantically similar documents
    """
    try:
        with httpx.Client(timeout=HTTP_TIMEOUT) as client:
            response = client.post(
                f"{RAG_SERVER_URL}/search/semantic",
                params={"query": query, "top_k": top_k},
            )
            response.raise_for_status()
            data = response.json()

        results = data.get("results", [])
        return _format_search_results(results, "semantic")

    except Exception as e:
        error_msg = f"Error in semantic search: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise ValueError(error_msg) from e


@mcp.tool()
def search_hybrid(query: str, top_k: int = 5) -> str:
    """
    Hybrid search combining BM25 keywords and semantic similarity.

    Uses Reciprocal Rank Fusion (RRF) to combine results from both methods.
    Best for: General queries, balanced accuracy, when unsure which method to use.
    Speed: Moderate (slower than keyword, faster than semantic alone)

    Args:
        query: The search query
        top_k: Number of results to return (default: 5, max: 20)

    Returns:
        Formatted string with fused results from both search methods
    """
    try:
        with httpx.Client(timeout=HTTP_TIMEOUT) as client:
            response = client.post(
                f"{RAG_SERVER_URL}/search/hybrid",
                params={"query": query, "top_k": top_k},
            )
            response.raise_for_status()
            data = response.json()

        results = data.get("results", [])
        return _format_search_results(results, "hybrid (BM25 + Semantic)")

    except Exception as e:
        error_msg = f"Error in hybrid search: {str(e)}"
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
