#!/usr/bin/env python3
"""Log experiment results to BENCHMARK_RESULTS.md

Helper script to easily add new experiment runs to the benchmark document.

Usage:
    python scripts/log_experiment.py --experiment retrieval \\
        --date 2025-05-31 \\
        --results retrieval_results.json \\
        --summary "Greppy is 2.24ms latency, 75% relevant"

    python scripts/log_experiment.py --experiment claude-api \\
        --date 2025-05-31 \\
        --results evaluation_results.json \\
        --summary "Greppy is 65% cheaper and 57% faster"
"""

import json
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


def load_json_results(filepath: str) -> dict:
    """Load results from JSON file."""
    try:
        with open(filepath) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Results file not found: {filepath}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {filepath}")
        sys.exit(1)


def generate_retrieval_summary(results: list) -> str:
    """Generate summary table from retrieval results."""
    if not results:
        return ""

    # Group by search method
    by_method = {}
    for r in results:
        method = r.get("search_method", "Unknown")
        if method not in by_method:
            by_method[method] = []
        by_method[method].append(r)

    output = []

    for method in sorted(by_method.keys()):
        method_results = by_method[method]

        output.append(f"\n**{method}**\n")
        output.append("| Query | Latency (ms) | Results | Tokens | Relevance |")
        output.append("|-------|--------------|---------|--------|-----------|")

        for r in method_results:
            latency = f"{r.get('latency_ms', 0):.2f}"
            tokens = r.get("total_tokens", 0)
            relevance = f"{r.get('relevance_score', 0)*100:.0f}%"
            query = r.get("query_text", "")[:20]

            output.append(
                f"| {query} | {latency} | {r.get('num_results', 0)} | {tokens} | {relevance} |"
            )

        # Calculate averages
        avg_latency = sum(r.get("latency_ms", 0) for r in method_results) / len(method_results)
        avg_tokens = sum(r.get("total_tokens", 0) for r in method_results) / len(method_results)
        avg_relevance = sum(r.get("relevance_score", 0) for r in method_results) / len(
            method_results
        )

        output.append(f"\n**{method} Average:** {avg_latency:.2f}ms, {avg_tokens:.0f} tokens, {avg_relevance*100:.0f}% relevance\n")

    return "\n".join(output)


def generate_claude_summary(results: list) -> str:
    """Generate summary table from Claude API evaluation results."""
    if not results:
        return ""

    # Group by task
    by_task = {}
    for r in results:
        task_id = r.get("task_id", "unknown")
        if task_id not in by_task:
            by_task[task_id] = {}
        mode = r.get("mode", "unknown")
        by_task[task_id][mode] = r

    output = []

    for task_id in sorted(by_task.keys()):
        task = by_task[task_id]
        greppy = task.get("greppy", {})
        native = task.get("native", {})

        if not greppy or not native:
            continue

        output.append(f"\n**{task_id}**\n")
        output.append("| Metric | Greppy | Native | Improvement |")
        output.append("|--------|--------|--------|-------------|")

        # Token comparison
        greppy_tokens = greppy.get("total_tokens", 0)
        native_tokens = native.get("total_tokens", 0)
        improvement = (
            (native_tokens - greppy_tokens) / native_tokens * 100
            if native_tokens > 0
            else 0
        )
        output.append(
            f"| Tokens | {greppy_tokens:,} | {native_tokens:,} | {improvement:+.0f}% |"
        )

        # Latency comparison
        greppy_latency = greppy.get("latency_seconds", 0)
        native_latency = native.get("latency_seconds", 0)
        improvement = (
            (native_latency - greppy_latency) / native_latency * 100
            if native_latency > 0
            else 0
        )
        output.append(
            f"| Latency | {greppy_latency:.2f}s | {native_latency:.2f}s | {improvement:+.0f}% |"
        )

        # Cost comparison
        greppy_cost = greppy.get("cost", 0)
        native_cost = native.get("cost", 0)
        improvement = (native_cost - greppy_cost) / native_cost * 100 if native_cost > 0 else 0
        output.append(
            f"| Cost | ${greppy_cost:.3f} | ${native_cost:.3f} | {improvement:+.0f}% |"
        )

    return "\n".join(output)


def create_experiment_section(
    experiment_type: str,
    date: str,
    summary: str,
    results_data: Optional[list] = None,
) -> str:
    """Create a new experiment section for the benchmark document."""

    if experiment_type == "retrieval":
        results_summary = generate_retrieval_summary(results_data or [])
        title = "Retrieval Performance"
        detail = results_summary or "(Results pending)"
    elif experiment_type == "claude-api":
        results_summary = generate_claude_summary(results_data or [])
        title = "Claude API Evaluation"
        detail = results_summary or "(Results pending)"
    else:
        title = experiment_type
        detail = "(Custom experiment)"

    section = f"""
## {title} Results

**Date:** {date}
**Status:** ✅ Completed

### Summary

{summary}

### Detailed Results

{detail}

### Next Steps

Run the evaluation script to see full details:

**Retrieval:**
```bash
python scripts/evaluate_retrieval.py
```

**Claude API:**
```bash
export ANTHROPIC_API_KEY=sk-ant-...
python scripts/evaluate_greppy.py
```
"""

    return section


def update_benchmark_document(
    experiment_type: str,
    date: str,
    summary: str,
    results_data: Optional[list] = None,
) -> bool:
    """Update BENCHMARK_RESULTS.md with new results."""

    benchmark_file = Path("BENCHMARK_RESULTS.md")

    if not benchmark_file.exists():
        print(f"Error: {benchmark_file} not found")
        return False

    with open(benchmark_file, encoding='utf-8') as f:
        content = f.read()

    # Create new section
    new_section = create_experiment_section(experiment_type, date, summary, results_data)

    # Find insertion point (before "## Experiment N:" sections or at end)
    insertion_marker = "\n## Experiment"
    if insertion_marker in content:
        insert_pos = content.rfind(insertion_marker)
        # Find the next heading at the same level
        while insert_pos > 0:
            insert_pos = content.rfind("\n## ", 0, insert_pos) + 1
            if insert_pos <= 0:
                insert_pos = len(content)
                break
    else:
        # Insert before References section
        insert_pos = content.find("\n## References")
        if insert_pos < 0:
            insert_pos = len(content)

    # Insert new section
    updated_content = content[:insert_pos] + new_section + "\n" + content[insert_pos:]

    with open(benchmark_file, "w", encoding='utf-8') as f:
        f.write(updated_content)

    print(f"[+] Updated {benchmark_file}")
    print(f"    Date: {date}")
    print(f"    Summary: {summary}")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Log experiment results to BENCHMARK_RESULTS.md"
    )
    parser.add_argument(
        "--experiment",
        choices=["retrieval", "claude-api", "semantic-vs-keyword", "mode-switching"],
        required=True,
        help="Type of experiment",
    )
    parser.add_argument(
        "--date",
        default=datetime.now().strftime("%Y-%m-%d"),
        help="Date of experiment (default: today)",
    )
    parser.add_argument(
        "--results",
        help="Path to JSON results file",
    )
    parser.add_argument(
        "--summary",
        required=True,
        help="Summary of results",
    )

    args = parser.parse_args()

    # Load results if provided
    results_data = None
    if args.results:
        results_data = load_json_results(args.results)

    # Update document
    success = update_benchmark_document(
        args.experiment,
        args.date,
        args.summary,
        results_data,
    )

    if success:
        print("\nTip: Run 'git add BENCHMARK_RESULTS.md && git commit' to save results")
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
