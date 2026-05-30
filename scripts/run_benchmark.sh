#!/bin/bash

# Greppy Evaluation Suite Runner
# Runs all evaluation scripts with sensible defaults

set -e

cd "$(dirname "$0")/.."

echo "=========================================="
echo "Greppy Evaluation Suite"
echo "=========================================="
echo ""

# Check if index exists
if [ ! -f "bm25_db/corpus.jsonl" ]; then
    echo "Error: Greppy index not found."
    echo "Please run: atlas greppy index ."
    exit 1
fi

echo "Index found. Starting evaluations..."
echo ""

# Retrieval evaluation (no API key needed)
echo "[1/2] Running retrieval performance evaluation..."
echo "      Measures: latency, token overhead, relevance"
echo ""
python scripts/evaluate_retrieval.py --queries 5 --mode all
echo ""

# Claude API evaluation (if API key is set)
if [ -n "$ANTHROPIC_API_KEY" ] || [ -n "$OPENAI_API_KEY" ]; then
    echo "[2/2] Running Claude API evaluation..."
    echo "      Measures: token usage, latency, cost with vs without Greppy"
    echo ""
    python scripts/evaluate_greppy.py
else
    echo "[2/2] Skipping Claude API evaluation (ANTHROPIC_API_KEY not set)"
    echo "      To run: export ANTHROPIC_API_KEY=sk-ant-... && python scripts/evaluate_greppy.py"
fi

echo ""
echo "=========================================="
echo "Evaluation complete!"
echo "=========================================="
echo ""
echo "Results saved to:"
echo "  - retrieval_results.json"
echo "  - evaluation_results.json (if API key was set)"
echo ""
