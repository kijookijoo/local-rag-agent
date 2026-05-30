"""Evaluate Greppy retrieval performance by measuring search quality and speed.

Measures:
- Search latency (time to retrieve results)
- Result quality (relevance of results)
- Token overhead (context size of results)
- Comparison: BM25 vs Semantic vs Hybrid search

Usage:
    python scripts/evaluate_retrieval.py [--mode {semantic,keyword,hybrid,all}] [--queries N]
"""

import time
import json
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List
import argparse
from collections import defaultdict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.atlas.bm25store import BM25Store
from src.atlas.vectorstore import VectorStore
from src.atlas.greppy import Greppy
from rich.console import Console
from rich.table import Table

console = Console()

# Test queries focused on code understanding
TEST_QUERIES = [
    {
        "id": "auth",
        "query": "authentication",
        "semantic_query": "how are users authenticated",
        "expected_keywords": ["auth", "login", "password", "credential"],
    },
    {
        "id": "search",
        "query": "search retrieval",
        "semantic_query": "finding and retrieving information",
        "expected_keywords": ["search", "retrieve", "query", "result"],
    },
    {
        "id": "index",
        "query": "indexing",
        "semantic_query": "building search indexes for fast lookups",
        "expected_keywords": ["index", "chunk", "vector", "bm25"],
    },
    {
        "id": "error",
        "query": "error handling exceptions",
        "semantic_query": "how are errors caught and handled",
        "expected_keywords": ["error", "exception", "try", "catch"],
    },
    {
        "id": "data",
        "query": "data storage persistence",
        "semantic_query": "where is data stored and retrieved",
        "expected_keywords": ["store", "save", "persist", "database"],
    },
]


@dataclass
class RetrievalResult:
    """Result of a single search evaluation."""
    query_id: str
    query_text: str
    search_method: str
    num_results: int
    latency_ms: float
    avg_result_size: int
    total_tokens: int  # Estimated tokens in results
    relevance_score: float  # 0-1, based on expected keywords

    @property
    def tokens_per_second(self) -> float:
        if self.latency_ms == 0:
            return 0
        return (self.total_tokens / (self.latency_ms / 1000))


def estimate_tokens(text: str) -> int:
    """Estimate token count using simple heuristic: 1 token per 4 chars."""
    return max(1, len(text) // 4)


def score_relevance(result_text: str, expected_keywords: List[str]) -> float:
    """Score result relevance based on presence of expected keywords."""
    if not result_text:
        return 0.0

    text_lower = result_text.lower()
    found = sum(1 for kw in expected_keywords if kw.lower() in text_lower)
    return found / len(expected_keywords) if expected_keywords else 0.0


def evaluate_bm25(queries: List[dict], limit: int = 10) -> List[RetrievalResult]:
    """Evaluate BM25 keyword search."""
    console.print("[cyan]Evaluating BM25 keyword search...[/cyan]")

    bm25_store = BM25Store()
    if not bm25_store.corpus:
        console.print("[red]Error: BM25 index is empty. Run 'atlas greppy index .' first.[/red]")
        return []

    results = []
    for query in queries:
        start = time.perf_counter()
        docs = bm25_store.search(query["query"], k=limit)
        latency = (time.perf_counter() - start) * 1000  # Convert to ms

        result_text = "\n".join([d.page_content for d in docs])
        total_tokens = estimate_tokens(result_text)
        avg_size = len(result_text) // max(1, len(docs))
        relevance = score_relevance(result_text, query["expected_keywords"])

        results.append(
            RetrievalResult(
                query_id=query["id"],
                query_text=query["query"],
                search_method="BM25",
                num_results=len(docs),
                latency_ms=latency,
                avg_result_size=avg_size,
                total_tokens=total_tokens,
                relevance_score=relevance,
            )
        )

    return results


def evaluate_semantic(queries: List[dict], limit: int = 10) -> List[RetrievalResult]:
    """Evaluate semantic vector search."""
    console.print("[cyan]Evaluating semantic search...[/cyan]")

    try:
        vector_store = VectorStore()
        if vector_store.db._collection.count() == 0:
            console.print("[yellow]Warning: Vector store is empty. Run 'atlas greppy index .' first.[/yellow]")
            return []
    except Exception as e:
        console.print(f"[yellow]Warning: Vector store unavailable ({type(e).__name__}). Skipping semantic search.[/yellow]")
        return []

    results = []
    for query in queries:
        try:
            start = time.perf_counter()
            retriever = vector_store.as_retriever(k=limit)
            docs = retriever.invoke(query["semantic_query"])
            latency = (time.perf_counter() - start) * 1000

            result_text = "\n".join([d.page_content for d in docs])
            total_tokens = estimate_tokens(result_text)
            avg_size = len(result_text) // max(1, len(docs))
            relevance = score_relevance(result_text, query["expected_keywords"])

            results.append(
                RetrievalResult(
                    query_id=query["id"],
                    query_text=query["semantic_query"],
                    search_method="Semantic",
                    num_results=len(docs),
                    latency_ms=latency,
                    avg_result_size=avg_size,
                    total_tokens=total_tokens,
                    relevance_score=relevance,
                )
            )
        except Exception as e:
            console.print(f"[yellow]Skipping semantic search for {query['id']}: {e}[/yellow]")

    return results


def evaluate_hybrid(queries: List[dict], limit: int = 10) -> List[RetrievalResult]:
    """Evaluate hybrid search (Greppy's automatic fallback)."""
    console.print("[cyan]Evaluating hybrid search (Greppy)...[/cyan]")

    greppy = Greppy()
    results = []

    for query in queries:
        start = time.perf_counter()
        search_results = greppy.search(query["query"], limit=limit)
        latency = (time.perf_counter() - start) * 1000

        result_text = "\n".join([r["content"] for r in search_results])
        total_tokens = estimate_tokens(result_text)
        avg_size = len(result_text) // max(1, len(search_results))
        relevance = score_relevance(result_text, query["expected_keywords"])

        results.append(
            RetrievalResult(
                query_id=query["id"],
                query_text=query["query"],
                search_method="Hybrid (Greppy)",
                num_results=len(search_results),
                latency_ms=latency,
                avg_result_size=avg_size,
                total_tokens=total_tokens,
                relevance_score=relevance,
            )
        )

    return results


def print_results(results: List[RetrievalResult]):
    """Print results in a formatted table."""
    if not results:
        console.print("[yellow]No results to display[/yellow]")
        return

    # Group by search method
    by_method = defaultdict(list)
    for result in results:
        by_method[result.search_method].append(result)

    # Summary table by query
    console.print("\n[bold cyan]Results by Query[/bold cyan]\n")

    for method in sorted(by_method.keys()):
        table = Table(title=f"{method} Search Performance")
        table.add_column("Query", style="cyan")
        table.add_column("Latency (ms)", style="green")
        table.add_column("Results", style="magenta")
        table.add_column("Avg Size (chars)", style="yellow")
        table.add_column("Total Tokens", style="blue")
        table.add_column("Relevance", style="cyan")

        for result in by_method[method]:
            relevance_pct = f"{result.relevance_score*100:.0f}%"
            table.add_row(
                result.query_text[:30],
                f"{result.latency_ms:.2f}",
                str(result.num_results),
                str(result.avg_result_size),
                str(result.total_tokens),
                relevance_pct,
            )

        console.print(table)

    # Comparison summary
    console.print("\n[bold cyan]Summary Comparison[/bold cyan]\n")

    summary_table = Table(title="Average Metrics by Search Method")
    summary_table.add_column("Method", style="cyan")
    summary_table.add_column("Avg Latency (ms)", style="green")
    summary_table.add_column("Avg Relevance", style="magenta")
    summary_table.add_column("Avg Tokens", style="yellow")
    summary_table.add_column("Latency/Token", style="blue")

    for method in sorted(by_method.keys()):
        method_results = by_method[method]
        avg_latency = sum(r.latency_ms for r in method_results) / len(method_results)
        avg_relevance = sum(r.relevance_score for r in method_results) / len(method_results)
        avg_tokens = sum(r.total_tokens for r in method_results) / len(method_results)

        summary_table.add_row(
            method,
            f"{avg_latency:.2f}",
            f"{avg_relevance*100:.0f}%",
            f"{avg_tokens:.0f}",
            f"{avg_latency/avg_tokens:.3f}" if avg_tokens > 0 else "N/A",
        )

    console.print(summary_table)

    # Save to JSON
    results_file = Path("retrieval_results.json")
    results_data = [
        {
            "query_id": r.query_id,
            "query_text": r.query_text,
            "search_method": r.search_method,
            "num_results": r.num_results,
            "latency_ms": r.latency_ms,
            "avg_result_size": r.avg_result_size,
            "total_tokens": r.total_tokens,
            "relevance_score": r.relevance_score,
        }
        for r in results
    ]
    with open(results_file, "w") as f:
        json.dump(results_data, f, indent=2)
    console.print(f"\n[dim]Results saved to {results_file}[/dim]\n")


def main():
    parser = argparse.ArgumentParser(description="Evaluate Greppy retrieval performance")
    parser.add_argument(
        "--mode",
        choices=["semantic", "keyword", "hybrid", "all"],
        default="all",
        help="Search methods to evaluate (default: all)"
    )
    parser.add_argument(
        "--queries",
        type=int,
        default=len(TEST_QUERIES),
        help=f"Number of test queries (default: {len(TEST_QUERIES)})"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of results per query (default: 10)"
    )

    args = parser.parse_args()

    queries = TEST_QUERIES[:args.queries]

    console.print("[bold cyan]Greppy Retrieval Evaluation[/bold cyan]\n")
    console.print(f"Test queries: {len(queries)}")
    console.print(f"Results per query: {args.limit}")
    console.print(f"Evaluation mode: {args.mode}\n")

    all_results = []

    if args.mode in ["keyword", "all"]:
        all_results.extend(evaluate_bm25(queries, limit=args.limit))

    if args.mode in ["semantic", "all"]:
        all_results.extend(evaluate_semantic(queries, limit=args.limit))

    if args.mode in ["hybrid", "all"]:
        all_results.extend(evaluate_hybrid(queries, limit=args.limit))

    print_results(all_results)


if __name__ == "__main__":
    main()
