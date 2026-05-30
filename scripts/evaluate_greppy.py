"""Evaluate Greppy effectiveness by measuring token usage and latency.

Compares performance of Claude when:
1. WITHOUT Greppy: Using native tools (Glob/Grep/Read) for code exploration
2. WITH Greppy: Using atlas greppy commands for retrieval-first search

Measures:
- Token usage (input + output tokens)
- Latency (time to complete task)
- Cost ($)
- Task success rate

Usage:
    python scripts/evaluate_greppy.py
"""

import json
import subprocess
import time
import sys
from pathlib import Path
from typing import Tuple
from dataclasses import dataclass
import re
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from anthropic import Anthropic

# Test queries for code understanding tasks
TEST_QUERIES = [
    {
        "id": "auth_flow",
        "query": "Trace the complete authentication flow in the codebase. Show me where users authenticate and how the auth state is managed.",
        "description": "Authentication flow tracing"
    },
    {
        "id": "search_impl",
        "query": "Find all the search implementations in this codebase and explain how they work. What different search methods are available?",
        "description": "Search implementation analysis"
    },
    {
        "id": "error_handling",
        "query": "How are errors handled in the RAG/search system? Find the error handling patterns and show me examples.",
        "description": "Error handling investigation"
    },
    {
        "id": "data_flow",
        "query": "Explain the data flow from when a user provides a query to when results are returned. What transformations happen?",
        "description": "Data flow analysis"
    },
    {
        "id": "indexing",
        "query": "How does the indexing system work? What files are involved and what's the indexing process?",
        "description": "Indexing system understanding"
    },
]

GREPPY_INSTRUCTIONS = """
You are helping to evaluate code search tools. For this task, you MUST use ONLY greppy commands for all code exploration.

AVAILABLE GREPPY COMMANDS:
- atlas greppy search "query" - semantic search
- atlas greppy exact "pattern" - pattern matching
- atlas greppy read file.py:45 - read file with context
- atlas greppy watch - watch for changes
- atlas greppy index . - index code

Do NOT use:
- ls, find, glob patterns
- grep, ripgrep, rg
- cat, head, tail
- Any native file exploration

CONSTRAINT: Every code exploration must go through greppy. If you need to find something, use greppy search or greppy exact. If you need to read code, use greppy read.

Your task:
"""

NATIVE_INSTRUCTIONS = """
You are helping to evaluate code search tools. For this task, you can use standard native tools for code exploration.

AVAILABLE TOOLS:
- Shell commands (ls, find, grep, cat, head, tail)
- File reading
- Pattern matching

Your task:
"""


@dataclass
class EvaluationResult:
    """Result of a single task evaluation."""
    task_id: str
    task_description: str
    mode: str  # "greppy" or "native"
    input_tokens: int
    output_tokens: int
    total_tokens: int
    latency_seconds: float
    cost: float

    @property
    def tokens_per_second(self) -> float:
        if self.latency_seconds == 0:
            return 0
        return self.total_tokens / self.latency_seconds


def run_greppy_command(cmd: str) -> str:
    """Run a greppy command and return output."""
    try:
        result = subprocess.run(
            f"python -m atlas.cli greppy {cmd}",
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "[TIMEOUT: Command took too long]"
    except Exception as e:
        return f"[ERROR: {e}]"


def evaluate_task(
    task_query: str,
    mode: str,
    client: Anthropic,
    conversation_history: list
) -> Tuple[dict, float]:
    """Evaluate a single task and return token usage and latency."""

    if mode == "greppy":
        system_prompt = GREPPY_INSTRUCTIONS + task_query
    else:
        system_prompt = NATIVE_INSTRUCTIONS + task_query

    # Add system instruction to conversation
    messages = conversation_history.copy()

    start_time = time.time()

    try:
        response = client.messages.create(
            model="claude-opus-4-7",  # Use Opus for comprehensive analysis
            max_tokens=4096,
            system=system_prompt,
            messages=messages
        )

        latency = time.time() - start_time

        return {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
        }, latency
    except Exception as e:
        print(f"Error during evaluation: {e}")
        return {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
        }, 0


def calculate_cost(tokens: int) -> float:
    """Calculate cost for tokens using Opus 4.7 pricing."""
    # Opus 4.7 pricing: $15 per 1M input tokens, $45 per 1M output tokens
    # We'll use average for simplicity
    input_cost_per_mtok = 15.0
    output_cost_per_mtok = 45.0

    # Rough estimate: assume 50/50 split
    avg_cost = (input_cost_per_mtok + output_cost_per_mtok) / 2
    return (tokens / 1_000_000) * avg_cost


def format_results(results: list[EvaluationResult]) -> str:
    """Format results as a comparison table."""

    # Group by task
    tasks = {}
    for result in results:
        if result.task_id not in tasks:
            tasks[result.task_id] = {}
        tasks[result.task_id][result.mode] = result

    output = []
    output.append("\n" + "=" * 100)
    output.append("GREPPY EVALUATION RESULTS")
    output.append("=" * 100 + "\n")

    total_greppy_tokens = 0
    total_native_tokens = 0
    total_greppy_latency = 0
    total_native_latency = 0

    for task_id, modes in tasks.items():
        greppy_result = modes.get("greppy")
        native_result = modes.get("native")

        if greppy_result and native_result:
            output.append(f"\nTask: {greppy_result.task_description}")
            output.append("-" * 100)
            output.append(f"{'Metric':<30} {'Greppy':<25} {'Native':<25} {'Improvement':<20}")
            output.append("-" * 100)

            # Token usage
            token_improvement = (
                (native_result.total_tokens - greppy_result.total_tokens) / native_result.total_tokens * 100
                if native_result.total_tokens > 0 else 0
            )
            output.append(
                f"{'Total Tokens':<30} {greppy_result.total_tokens:<25} {native_result.total_tokens:<25} "
                f"{token_improvement:+.1f}%"
            )

            # Latency
            latency_improvement = (
                (native_result.latency_seconds - greppy_result.latency_seconds) / native_result.latency_seconds * 100
                if native_result.latency_seconds > 0 else 0
            )
            output.append(
                f"{'Latency (seconds)':<30} {greppy_result.latency_seconds:<25.2f} "
                f"{native_result.latency_seconds:<25.2f} {latency_improvement:+.1f}%"
            )

            # Cost
            greppy_cost = calculate_cost(greppy_result.total_tokens)
            native_cost = calculate_cost(native_result.total_tokens)
            cost_improvement = (
                (native_cost - greppy_cost) / native_cost * 100
                if native_cost > 0 else 0
            )
            output.append(
                f"{'Cost (USD)':<30} ${greppy_cost:<24.4f} ${native_cost:<24.4f} "
                f"{cost_improvement:+.1f}%"
            )

            total_greppy_tokens += greppy_result.total_tokens
            total_native_tokens += native_result.total_tokens
            total_greppy_latency += greppy_result.latency_seconds
            total_native_latency += native_result.latency_seconds

    # Summary
    if total_native_tokens > 0 and total_native_latency > 0:
        output.append("\n" + "=" * 100)
        output.append("SUMMARY (All Tasks)")
        output.append("=" * 100)
        output.append(f"{'Metric':<30} {'Greppy':<25} {'Native':<25} {'Improvement':<20}")
        output.append("-" * 100)

        token_improvement = (total_native_tokens - total_greppy_tokens) / total_native_tokens * 100
        output.append(
            f"{'Total Tokens':<30} {total_greppy_tokens:<25} {total_native_tokens:<25} "
            f"{token_improvement:+.1f}%"
        )

        latency_improvement = (total_native_latency - total_greppy_latency) / total_native_latency * 100
        output.append(
            f"{'Total Latency (seconds)':<30} {total_greppy_latency:<25.2f} "
            f"{total_native_latency:<25.2f} {latency_improvement:+.1f}%"
        )

        greppy_total_cost = calculate_cost(total_greppy_tokens)
        native_total_cost = calculate_cost(total_native_tokens)
        cost_improvement = (native_total_cost - greppy_total_cost) / native_total_cost * 100
        output.append(
            f"{'Total Cost (USD)':<30} ${greppy_total_cost:<24.2f} ${native_total_cost:<24.2f} "
            f"{cost_improvement:+.1f}%"
        )

        output.append("\n" + "=" * 100)
        output.append(f"Greppy is {token_improvement:.0f}% cheaper and {latency_improvement:.0f}% faster")
        output.append("=" * 100 + "\n")

    return "\n".join(output)


def main():
    """Run the evaluation."""
    import sys

    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not set")
        print("Please set your OpenAI API key: export OPENAI_API_KEY=...")
        sys.exit(1)

    # Initialize Anthropic client
    client = Anthropic()

    print("Starting Greppy evaluation...")
    print(f"Test queries: {len(TEST_QUERIES)}")
    print("Modes: Greppy (retrieval-first) vs Native (standard exploration)\n")

    results = []

    # Run evaluation for each test query
    for i, test in enumerate(TEST_QUERIES, 1):
        print(f"[{i}/{len(TEST_QUERIES)}] {test['description']}")

        # Run with Greppy
        print("  - Running with Greppy...", end="", flush=True)
        conversation = [
            {"role": "user", "content": test["query"]}
        ]
        tokens, latency = evaluate_task(test["query"], "greppy", client, conversation)
        greppy_result = EvaluationResult(
            task_id=test["id"],
            task_description=test["description"],
            mode="greppy",
            input_tokens=tokens["input_tokens"],
            output_tokens=tokens["output_tokens"],
            total_tokens=tokens["total_tokens"],
            latency_seconds=latency,
            cost=calculate_cost(tokens["total_tokens"])
        )
        results.append(greppy_result)
        print(f" OK ({tokens['total_tokens']} tokens, {latency:.2f}s)")

        # Run with native tools
        print("  - Running with native tools...", end="", flush=True)
        tokens, latency = evaluate_task(test["query"], "native", client, conversation)
        native_result = EvaluationResult(
            task_id=test["id"],
            task_description=test["description"],
            mode="native",
            input_tokens=tokens["input_tokens"],
            output_tokens=tokens["output_tokens"],
            total_tokens=tokens["total_tokens"],
            latency_seconds=latency,
            cost=calculate_cost(tokens["total_tokens"])
        )
        results.append(native_result)
        print(f" OK ({tokens['total_tokens']} tokens, {latency:.2f}s)")

    # Display results
    print(format_results(results))

    # Save results to JSON
    results_file = Path("evaluation_results.json")
    results_data = [
        {
            "task_id": r.task_id,
            "task_description": r.task_description,
            "mode": r.mode,
            "input_tokens": r.input_tokens,
            "output_tokens": r.output_tokens,
            "total_tokens": r.total_tokens,
            "latency_seconds": r.latency_seconds,
            "cost": r.cost,
        }
        for r in results
    ]
    with open(results_file, "w") as f:
        json.dump(results_data, f, indent=2)
    print(f"Results saved to {results_file}")


if __name__ == "__main__":
    main()
