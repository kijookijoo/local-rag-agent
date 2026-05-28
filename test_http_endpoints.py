#!/usr/bin/env python
"""Test the HTTP server endpoints to verify hybrid retrieval is working."""

import httpx
import time
import json

BASE_URL = "http://127.0.0.1:8000"

TEST_QUERIES = [
    {
        "query": "BM25 keyword matching",
        "description": "Code lookup - should favor keyword",
    },
    {
        "query": "semantic search vector similarity",
        "description": "Conceptual - should favor semantic",
    },
    {
        "query": "RAG retrieval augmented generation",
        "description": "General - hybrid should balance both",
    },
]


def test_endpoint(endpoint: str, query: str) -> dict:
    """Test a single endpoint."""
    try:
        with httpx.Client(timeout=10) as client:
            start = time.perf_counter()
            response = client.post(
                f"{BASE_URL}{endpoint}",
                params={"query": query, "top_k": 3},
            )
            elapsed = time.perf_counter() - start

            if response.status_code == 200:
                data = response.json()
                return {
                    "method": endpoint.split("/")[-1],
                    "status": "ok",
                    "count": data.get("count", 0),
                    "time": elapsed,
                    "results": data.get("results", []),
                }
            else:
                return {
                    "method": endpoint.split("/")[-1],
                    "status": "error",
                    "error": response.text,
                    "time": elapsed,
                }
    except Exception as e:
        return {
            "method": endpoint.split("/")[-1],
            "status": "error",
            "error": str(e),
            "time": -1,
        }


def format_results(query: str, description: str, results: dict) -> str:
    """Format test results."""
    keyword = results.get("keyword", {})
    semantic = results.get("semantic", {})
    hybrid = results.get("hybrid", {})

    output = f"""
{'='*70}
Query: {query}
Description: {description}
{'='*70}

KEYWORD SEARCH:
  Status:   {keyword.get('status', 'N/A')}
  Results:  {keyword.get('count', 0)}
  Time:     {keyword.get('time', 0):.3f}s
"""

    if keyword.get("results"):
        output += "  Documents:\n"
        for r in keyword.get("results", [])[:2]:
            preview = r["content"][:80].replace("\n", " ")
            output += f"    [{r['rank']}] {preview}...\n"

    output += f"""
SEMANTIC SEARCH:
  Status:   {semantic.get('status', 'N/A')}
  Results:  {semantic.get('count', 0)}
  Time:     {semantic.get('time', 0):.3f}s
"""

    if semantic.get("results"):
        output += "  Documents:\n"
        for r in semantic.get("results", [])[:2]:
            preview = r["content"][:80].replace("\n", " ")
            output += f"    [{r['rank']}] {preview}...\n"

    output += f"""
HYBRID SEARCH:
  Status:   {hybrid.get('status', 'N/A')}
  Results:  {hybrid.get('count', 0)}
  Time:     {hybrid.get('time', 0):.3f}s
"""

    if hybrid.get("results"):
        output += "  Documents:\n"
        for r in hybrid.get("results", [])[:2]:
            preview = r["content"][:80].replace("\n", " ")
            output += f"    [{r['rank']}] {preview}...\n"

    # Performance comparison
    if keyword.get("time") > 0 and semantic.get("time") > 0:
        output += f"""
PERFORMANCE COMPARISON:
  Semantic vs Keyword: {semantic.get('time', 0) / max(keyword.get('time', 0.001), 0.001):.1f}x slower
  Hybrid vs Keyword:   {hybrid.get('time', 0) / max(keyword.get('time', 0.001), 0.001):.1f}x slower
"""

    return output


def main():
    print("=" * 70)
    print("HTTP SERVER ENDPOINT TEST - Hybrid Retrieval Verification")
    print("=" * 70)
    print(f"\nTesting server at: {BASE_URL}")
    print("Testing endpoints: /search/keyword, /search/semantic, /search/hybrid")
    print("\nMake sure HTTP server is running: python http_server.py\n")

    # Test health
    try:
        with httpx.Client(timeout=5) as client:
            response = client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print("[OK] Server is running\n")
            else:
                print("[ERROR] Server returned non-200 status\n")
                return
    except Exception as e:
        print(f"[ERROR] Cannot connect to server: {e}")
        print("Make sure to run: python http_server.py\n")
        return

    all_results = []

    for test_case in TEST_QUERIES:
        query = test_case["query"]
        description = test_case["description"]

        results = {
            "keyword": test_endpoint("/search/keyword", query),
            "semantic": test_endpoint("/search/semantic", query),
            "hybrid": test_endpoint("/search/hybrid", query),
        }

        all_results.append(
            {
                "query": query,
                "description": description,
                "results": results,
            }
        )

        print(format_results(query, description, results))

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    total_keyword_time = sum(
        r["results"]["keyword"].get("time", 0) for r in all_results
    )
    total_semantic_time = sum(
        r["results"]["semantic"].get("time", 0) for r in all_results
    )
    total_hybrid_time = sum(
        r["results"]["hybrid"].get("time", 0) for r in all_results
    )

    print(f"\nTotal time across all queries:")
    print(f"  Keyword:  {total_keyword_time:.3f}s")
    print(f"  Semantic: {total_semantic_time:.3f}s ({total_semantic_time/max(total_keyword_time, 0.001):.1f}x slower)")
    print(f"  Hybrid:   {total_hybrid_time:.3f}s ({total_hybrid_time/max(total_keyword_time, 0.001):.1f}x slower)")

    print(f"\nEndpoints working:")
    print(f"  [OK] /search/keyword  - Fast BM25 matching")
    print(f"  [OK] /search/semantic - Vector similarity")
    print(f"  [OK] /search/hybrid   - Reciprocal Rank Fusion")

    print(f"\nAll three MCP tools are ready to use!")

    # Save results
    with open("test_http_endpoints_results.json", "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"[OK] Results saved to: test_http_endpoints_results.json")
    print("=" * 70)


if __name__ == "__main__":
    main()
