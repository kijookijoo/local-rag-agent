#!/usr/bin/env python
"""Performance testing suite for RAG MCP Server

Measures:
- Server startup time
- First search latency (models load)
- Subsequent search latency
- Memory usage
- Token efficiency
- Throughput
"""

import time
import psutil
import os
from typing import Dict, List, Tuple

from src.atlas.mcp_server import RAGService


class PerformanceTester:
    def __init__(self):
        self.results = {}
        self.process = psutil.Process(os.getpid())

    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage in MB"""
        info = self.process.memory_info()
        return {
            "rss_mb": info.rss / 1024 / 1024,  # Resident Set Size
            "vms_mb": info.vms / 1024 / 1024,  # Virtual Memory Size
        }

    def test_startup_time(self) -> float:
        """Measure server startup time"""
        print("\n[TEST] Server Startup Time")
        print("-" * 50)

        mem_before = self.get_memory_usage()
        print(f"Memory before: {mem_before['rss_mb']:.1f} MB")

        start = time.time()
        service = RAGService()
        startup_time = time.time() - start

        mem_after = self.get_memory_usage()
        mem_increase = mem_after["rss_mb"] - mem_before["rss_mb"]

        print(f"Startup time: {startup_time:.2f}s")
        print(f"Memory after: {mem_after['rss_mb']:.1f} MB")
        print(f"Memory increase: {mem_increase:.1f} MB")

        self.results["startup_time"] = startup_time
        self.results["memory_increase"] = mem_increase
        return startup_time

    def test_search_latency(self, service: RAGService, num_searches: int = 5):
        """Measure search latency"""
        print("\n[TEST] Search Latency")
        print("-" * 50)

        test_queries = [
            "authentication",
            "API endpoints",
            "error handling",
            "database",
            "security",
        ][:num_searches]

        latencies = []
        first_search = None

        for i, query in enumerate(test_queries):
            start = time.time()
            results = service.search(query, top_k=5)
            latency = time.time() - start
            latencies.append(latency)

            label = "FIRST (models load)" if i == 0 else "subsequent"
            print(f"  Query {i+1}: '{query[:30]:<30}' → {latency:.2f}s ({label})")

            if i == 0:
                first_search = latency

        avg_subsequent = sum(latencies[1:]) / len(latencies[1:]) if len(latencies) > 1 else 0

        print(f"\nSummary:")
        print(f"  First search (models load): {first_search:.2f}s")
        print(f"  Avg subsequent searches: {avg_subsequent:.2f}s")
        print(f"  Speedup: {first_search / max(avg_subsequent, 0.01):.1f}x faster")

        self.results["first_search_latency"] = first_search
        self.results["avg_subsequent_latency"] = avg_subsequent
        self.results["latencies"] = latencies

        return latencies

    def test_throughput(self, service: RAGService, duration_seconds: int = 10):
        """Measure queries per second"""
        print("\n[TEST] Throughput (Queries/Second)")
        print("-" * 50)

        queries = [
            "authentication",
            "database",
            "API",
            "security",
            "errors",
        ]

        start = time.time()
        query_count = 0
        current_query_idx = 0

        print(f"Running for {duration_seconds} seconds...")

        while time.time() - start < duration_seconds:
            query = queries[current_query_idx % len(queries)]
            try:
                service.search(query, top_k=3)
                query_count += 1
                current_query_idx += 1
            except Exception as e:
                print(f"Error during query: {e}")
                break

        elapsed = time.time() - start
        qps = query_count / elapsed

        print(f"Queries completed: {query_count}")
        print(f"Time elapsed: {elapsed:.1f}s")
        print(f"Throughput: {qps:.1f} queries/second")

        self.results["throughput_qps"] = qps
        self.results["query_count"] = query_count

        return qps

    def test_token_efficiency(self, service: RAGService):
        """Estimate token savings"""
        print("\n[TEST] Token Efficiency Analysis")
        print("-" * 50)

        # Simulate a search and measure context
        results = service.search("authentication", top_k=5)
        formatted = service.format_results(results)

        # Rough token estimation: ~4 characters per token
        context_tokens = len(formatted) // 4

        # Assume full document would be 100MB
        full_doc_tokens = 100_000_000 // 4  # Very rough estimate

        savings = (1 - context_tokens / max(full_doc_tokens, 1)) * 100

        print(f"Retrieved context tokens: ~{context_tokens:,}")
        print(f"Full document tokens: ~{full_doc_tokens:,}")
        print(f"Token savings: ~{savings:.1f}%")

        print(f"\nCost analysis (OpenAI rates):")
        print(f"  Without RAG: ${full_doc_tokens * 0.01 / 1_000_000:.4f}")
        print(f"  With RAG: ${context_tokens * 0.01 / 1_000_000:.4f}")

        self.results["estimated_token_savings"] = savings
        self.results["retrieved_context_tokens"] = context_tokens

        return savings

    def test_result_quality(self, service: RAGService):
        """Check result quality and metadata"""
        print("\n[TEST] Result Quality")
        print("-" * 50)

        results = service.search("authentication", top_k=3)

        print(f"Results returned: {len(results)}")
        for i, result in enumerate(results, 1):
            content_len = len(result["content"])
            metadata_keys = list(result.get("metadata", {}).keys())
            print(f"\n  Result {i}:")
            print(f"    Content length: {content_len} chars")
            print(f"    Metadata keys: {metadata_keys}")
            print(f"    Content preview: {result['content'][:100]}...")

        self.results["results_quality"] = len(results)

        return len(results)

    def print_summary(self):
        """Print comprehensive performance summary"""
        print("\n" + "=" * 60)
        print("PERFORMANCE TEST SUMMARY")
        print("=" * 60)

        if "startup_time" in self.results:
            print(f"\nStartup Performance:")
            print(f"  Startup time: {self.results['startup_time']:.2f}s")
            print(f"  Memory overhead: {self.results['memory_increase']:.1f} MB")

        if "first_search_latency" in self.results:
            print(f"\nSearch Latency:")
            print(f"  First search: {self.results['first_search_latency']:.2f}s")
            print(f"  Avg subsequent: {self.results['avg_subsequent_latency']:.2f}s")

        if "throughput_qps" in self.results:
            print(f"\nThroughput:")
            print(f"  Queries/second: {self.results['throughput_qps']:.1f}")

        if "estimated_token_savings" in self.results:
            print(f"\nToken Efficiency:")
            print(f"  Estimated savings: {self.results['estimated_token_savings']:.1f}%")
            print(f"  Retrieved tokens: ~{self.results['retrieved_context_tokens']:,}")

        if "results_quality" in self.results:
            print(f"\nResult Quality:")
            print(f"  Results per query: {self.results['results_quality']}")

        print("\n" + "=" * 60)

    def run_all_tests(self, full: bool = True):
        """Run all performance tests"""
        print("=" * 60)
        print("RAG MCP SERVER PERFORMANCE TEST SUITE")
        print("=" * 60)

        try:
            # Startup test
            self.test_startup_time()

            # Initialize service for remaining tests
            service = RAGService()

            # Search latency
            self.test_search_latency(service, num_searches=5)

            # Throughput test
            if full:
                self.test_throughput(service, duration_seconds=10)

            # Token efficiency
            self.test_token_efficiency(service)

            # Result quality
            self.test_result_quality(service)

            # Summary
            self.print_summary()

            return True

        except Exception as e:
            print(f"\n[ERROR] Test failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Test RAG server performance")
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick test (skip throughput test)",
    )
    parser.add_argument(
        "--latency-only",
        action="store_true",
        help="Only test search latency",
    )

    args = parser.parse_args()

    tester = PerformanceTester()

    if args.latency_only:
        service = RAGService()
        tester.test_search_latency(service, num_searches=5)
    else:
        tester.run_all_tests(full=not args.quick)


if __name__ == "__main__":
    main()
