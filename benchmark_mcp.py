#!/usr/bin/env python
"""Benchmark Claude API token usage with and without MCP server.

Measures token efficiency and execution time comparing:
1. Direct prompts without MCP context
2. Prompts using MCP search_rag tool for context
"""

import time
import json
import os
import random
from typing import Optional

# Try to import Anthropic SDK, fall back to simulation if unavailable
try:
    from anthropic import Anthropic

    client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    USE_REAL_API = True
except ImportError:
    client = None
    USE_REAL_API = False

# Test queries - well-written, realistic prompts
TEST_QUERIES = [
    {
        "name": "Code Architecture Question",
        "prompt": "I'm building a Python RAG system. What's the best way to structure the embedding pipeline to handle both semantic and keyword-based search? Should I use separate retrievers or combine them? What are the tradeoffs?",
        "mcp_query": "embedding pipeline architecture",
    },
    {
        "name": "Performance Optimization",
        "prompt": "We're getting slow search latency in our MCP server. What are the main factors that affect RAG search performance, and how can we optimize them? Specifically, should we focus on the embedding model, the retrieval strategy, or the chunk size?",
        "mcp_query": "search latency optimization performance tuning",
    },
    {
        "name": "Integration Pattern",
        "prompt": "How should we integrate a RAG system into Claude? Should we use MCP, tool calling, or inject context directly into prompts? What are the pros and cons of each approach?",
        "mcp_query": "MCP integration Claude tool calling RAG",
    },
]


def run_without_mcp(prompt: str) -> dict:
    """Run Claude query without MCP context."""
    print(f"  [WITHOUT MCP]")
    start_time = time.perf_counter()

    if USE_REAL_API and client:
        response = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=500,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        elapsed = time.perf_counter() - start_time

        return {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            "time_seconds": elapsed,
            "content": response.content[0].text,
        }
    else:
        # Simulate realistic token usage
        time.sleep(0.3)  # Simulate network latency
        elapsed = time.perf_counter() - start_time

        # Typical token counts for a well-answered question
        input_tokens = 200 + random.randint(-30, 50)
        output_tokens = 180 + random.randint(-40, 60)

        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "time_seconds": elapsed,
            "content": "This is a simulated response showing typical token usage patterns. In production, this would be Claude's actual response to your question.",
        }


def run_with_mcp(prompt: str, mcp_query: str) -> dict:
    """Run Claude query with MCP context."""
    print(f"  [WITH MCP] Running search for: '{mcp_query}'")
    start_time = time.perf_counter()

    if USE_REAL_API and client:
        messages = [
            {
                "role": "user",
                "content": prompt,
            }
        ]

        # First call to invoke the tool
        response = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=500,
            tools=[
                {
                    "name": "search_rag",
                    "description": "Search through indexed documents using the RAG pipeline.",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query for the RAG pipeline",
                            },
                            "top_k": {
                                "type": "integer",
                                "description": "Number of results to return (default: 5)",
                                "default": 5,
                            },
                        },
                        "required": ["query"],
                    },
                }
            ],
            messages=messages,
        )

        # Track tokens from first response
        first_input = response.usage.input_tokens
        first_output = response.usage.output_tokens

        # Check if tool was called
        if response.stop_reason == "tool_use":
            # Add assistant response and tool result
            messages.append({"role": "assistant", "content": response.content})

            # Simulate tool result
            tool_result = f"[Simulated MCP search results for '{mcp_query}']"
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": response.content[0].id,
                            "content": tool_result,
                        }
                    ],
                }
            )

            # Get final response
            final_response = client.messages.create(
                model="claude-opus-4-7",
                max_tokens=500,
                tools=[
                    {
                        "name": "search_rag",
                        "description": "Search through indexed documents using the RAG pipeline.",
                        "input_schema": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "The search query for the RAG pipeline",
                                },
                                "top_k": {
                                    "type": "integer",
                                    "description": "Number of results to return (default: 5)",
                                    "default": 5,
                                },
                            },
                            "required": ["query"],
                        },
                    }
                ],
                messages=messages,
            )

            total_input = first_input + final_response.usage.input_tokens
            total_output = first_output + final_response.usage.output_tokens
            content = final_response.content[0].text
        else:
            total_input = first_input
            total_output = first_output
            content = response.content[0].text

        elapsed = time.perf_counter() - start_time

        return {
            "input_tokens": total_input,
            "output_tokens": total_output,
            "total_tokens": total_input + total_output,
            "time_seconds": elapsed,
            "content": content[:200] + "..." if len(content) > 200 else content,
        }
    else:
        # Simulate MCP usage with tool calling overhead
        time.sleep(0.5)  # Simulate tool call latency
        elapsed = time.perf_counter() - start_time

        # Tool definition overhead (~100 tokens) + tool result overhead (~50 tokens)
        # Plus additional output tokens from using retrieved context
        input_tokens = 200 + 100 + random.randint(-30, 50)  # Tool overhead added
        output_tokens = 180 + 100 + random.randint(-40, 60)  # Additional context-aware output

        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "time_seconds": elapsed,
            "content": "Response with MCP context. This simulates what Claude would output after retrieving relevant documents from the RAG system.",
        }


def format_results(name: str, without_mcp: dict, with_mcp: dict) -> str:
    """Format benchmark results for display."""
    token_increase = (
        (with_mcp["total_tokens"] - without_mcp["total_tokens"])
        / without_mcp["total_tokens"]
        * 100
    )
    token_delta = with_mcp["total_tokens"] - without_mcp["total_tokens"]

    time_increase = (
        (with_mcp["time_seconds"] - without_mcp["time_seconds"])
        / without_mcp["time_seconds"]
        * 100
    )

    return f"""
+------------------------------------------------------------------+
| {name:<60} |
+------------------------------------------------------------------+

WITHOUT MCP:
  Input tokens:     {without_mcp["input_tokens"]:>6}
  Output tokens:    {without_mcp["output_tokens"]:>6}
  Total tokens:     {without_mcp["total_tokens"]:>6}
  Time:             {without_mcp["time_seconds"]:>6.2f}s

WITH MCP:
  Input tokens:     {with_mcp["input_tokens"]:>6}
  Output tokens:    {with_mcp["output_tokens"]:>6}
  Total tokens:     {with_mcp["total_tokens"]:>6}
  Time:             {with_mcp["time_seconds"]:>6.2f}s

COMPARISON:
  Token delta:      {token_delta:>+6} tokens ({token_increase:>+5.1f}%)
  Time delta:       {time_increase:>+5.1f}%
  Cost impact:      ${(with_mcp["total_tokens"] - without_mcp["total_tokens"]) * 0.003 / 1_000_000:>+.6f}
"""


def main():
    print("=" * 70)
    print("CLAUDE API TOKEN USAGE BENCHMARK: WITH vs WITHOUT MCP")
    print("=" * 70)
    print(f"\nModel: claude-opus-4-7")
    print(f"Test queries: {len(TEST_QUERIES)}")

    if USE_REAL_API:
        print("\n[OK] Using REAL Anthropic API")
    else:
        print("\n[INFO] Using SIMULATED results (Anthropic SDK not available)")
        print("  Install with: pip install anthropic")
        print("  Set ANTHROPIC_API_KEY environment variable")
    print("\nRunning benchmarks...\n")

    results = []

    for i, query_spec in enumerate(TEST_QUERIES, 1):
        print(f"\n[Query {i}/{len(TEST_QUERIES)}] {query_spec['name']}")
        print("-" * 70)

        try:
            # Run without MCP
            without_mcp = run_without_mcp(query_spec["prompt"])
            time.sleep(0.5)  # Brief delay between calls

            # Run with MCP
            with_mcp = run_with_mcp(query_spec["prompt"], query_spec["mcp_query"])

            results.append(
                {
                    "name": query_spec["name"],
                    "without_mcp": without_mcp,
                    "with_mcp": with_mcp,
                }
            )

            # Display results
            print(
                format_results(
                    query_spec["name"],
                    without_mcp,
                    with_mcp,
                )
            )
        except Exception as e:
            print(f"  ERROR: {e}")
            print("\n  Note: Make sure ANTHROPIC_API_KEY is set")
            return

    # Summary statistics
    print("\n" + "=" * 70)
    print("SUMMARY STATISTICS")
    print("=" * 70)

    total_tokens_without = sum(r["without_mcp"]["total_tokens"] for r in results)
    total_tokens_with = sum(r["with_mcp"]["total_tokens"] for r in results)
    total_time_without = sum(r["without_mcp"]["time_seconds"] for r in results)
    total_time_with = sum(r["with_mcp"]["time_seconds"] for r in results)

    avg_token_delta = (
        (total_tokens_with - total_tokens_without) / len(results)
    )
    token_increase_pct = (
        (total_tokens_with - total_tokens_without) / total_tokens_without * 100
    )
    time_increase_pct = (
        (total_time_with - total_time_without) / total_time_without * 100
    )

    cost_without = total_tokens_without * 0.003 / 1_000_000  # Opus rate
    cost_with = total_tokens_with * 0.003 / 1_000_000
    cost_delta = cost_with - cost_without

    print(f"\nTokens (aggregate):")
    print(f"  Without MCP:  {total_tokens_without:>7} tokens")
    print(f"  With MCP:     {total_tokens_with:>7} tokens")
    print(f"  Delta:        {total_tokens_with - total_tokens_without:>+7} tokens ({token_increase_pct:>+6.1f}%)")

    print(f"\nTime (aggregate):")
    print(f"  Without MCP:  {total_time_without:>7.2f}s")
    print(f"  With MCP:     {total_time_with:>7.2f}s")
    print(f"  Delta:        {time_increase_pct:>+6.1f}%")

    print(f"\nEstimated Cost (Opus rates):")
    print(f"  Without MCP:  ${cost_without:>8.6f}")
    print(f"  With MCP:     ${cost_with:>8.6f}")
    print(f"  Delta:        ${cost_delta:>+8.6f} ({(cost_delta/cost_without*100):>+6.1f}%)")

    print(f"\nAverage per query:")
    print(f"  Token delta:  {avg_token_delta:>+6.0f} tokens")
    print(f"  Avg time:     {total_time_with/len(results):>6.2f}s (with MCP)")

    # Save detailed results
    with open("benchmark_results.json", "w") as f:
        json.dump(
            {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "model": "claude-opus-4-7",
                "queries": results,
                "summary": {
                    "total_tokens_without": total_tokens_without,
                    "total_tokens_with": total_tokens_with,
                    "token_increase_pct": token_increase_pct,
                    "total_time_without": total_time_without,
                    "total_time_with": total_time_with,
                    "time_increase_pct": time_increase_pct,
                    "cost_without": cost_without,
                    "cost_with": cost_with,
                    "cost_delta": cost_delta,
                },
            },
            f,
            indent=2,
        )

    print(f"\n[OK] Detailed results saved to: benchmark_results.json")
    print("=" * 70)


if __name__ == "__main__":
    main()
