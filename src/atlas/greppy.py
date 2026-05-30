"""Greppy: Semantic code search CLI wrapping the RAG system.

Provides the same interface as Greppy (semantic search, exact matching, file reading)
but powered by the Atlas RAG engine (ChromaDB + BM25S).

Commands:
  greppy search "query" [-n N] [-p PATH]
  greppy exact "pattern" [-i] [-n N] [-p PATH]
  greppy read FILE[:LINE] [-c CONTEXT]
  greppy index [PATH] [--force]
  greppy watch [PATH] [--debounce SECONDS]
  greppy status [PATH]
  greppy clear
"""

import os
import re
import sys
from pathlib import Path
from typing import Optional, List, Tuple
import time

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .bm25store import BM25Store
from .vectorstore import VectorStore
from .chunker import chunk_docs
from .ingest import read_directory, to_langchain_docs
from .config import ALLOWED_EXTENSIONS, IGNORED_DIRS


class Greppy:
    """Greppy CLI interface wrapping Atlas RAG."""

    def __init__(self, project_path: Optional[str] = None):
        self.console = Console()
        self.project_path = Path(project_path or os.getcwd())
        self.bm25_store = BM25Store()
        self.vector_store = None
        try:
            self.vector_store = VectorStore()
        except Exception as e:
            self.console.print(
                f"[yellow]Warning: Semantic search unavailable ({type(e).__name__})[/yellow]"
            )
            self.console.print("[dim]Falling back to keyword-only search[/dim]")

    def search(self, query: str, limit: int = 10, path: Optional[str] = None) -> List[dict]:
        """Semantic search using vector embeddings (falls back to BM25 if unavailable).

        Args:
            query: Search query
            limit: Max number of results (1-20)
            path: Optional project path to search within

        Returns:
            List of result dicts with rank, content, and metadata
        """
        limit = min(max(limit, 1), 20)

        # Try semantic search first
        if self.vector_store:
            try:
                retriever = self.vector_store.as_retriever(k=limit)
                docs = retriever.invoke(query)
                results = []
                for idx, doc in enumerate(docs, 1):
                    results.append({
                        "rank": idx,
                        "content": doc.page_content,
                        "metadata": dict(doc.metadata),
                    })
                return results
            except Exception:
                pass

        # Fall back to BM25 keyword search
        docs = self.bm25_store.search(query, k=limit)
        return [
            {
                "rank": idx,
                "content": doc.page_content,
                "metadata": dict(doc.metadata),
            }
            for idx, doc in enumerate(docs, 1)
        ]

    def exact(
        self,
        pattern: str,
        limit: int = 20,
        path: Optional[str] = None,
        ignore_case: bool = False,
    ) -> List[dict]:
        """Exact pattern matching using BM25 or regex.

        Args:
            pattern: Pattern to search (regex or string)
            limit: Max number of results
            path: Optional project path
            ignore_case: Case-insensitive matching

        Returns:
            List of result dicts
        """
        limit = min(max(limit, 1), 20)

        try:
            # Try as regex first
            flags = re.IGNORECASE if ignore_case else 0
            regex = re.compile(pattern, flags)

            # Get all docs and filter by regex
            results = []
            for doc in self.bm25_store.corpus:
                content = doc["page_content"]
                matches = list(regex.finditer(content))

                if matches:
                    # Show context around first match
                    for match in matches[:1]:  # Just show first match per chunk
                        start = max(0, match.start() - 100)
                        end = min(len(content), match.end() + 100)
                        context = content[start:end]

                        results.append({
                            "rank": len(results) + 1,
                            "content": context,
                            "metadata": doc["metadata"],
                            "match": match.group(),
                        })

                    if len(results) >= limit:
                        break

            return results[:limit]
        except re.error:
            # Fall back to BM25 keyword search
            docs = self.bm25_store.search(pattern, k=limit)
            return [
                {
                    "rank": idx,
                    "content": doc.page_content,
                    "metadata": dict(doc.metadata),
                }
                for idx, doc in enumerate(docs, 1)
            ]

    def read(self, location: str, context: int = 50) -> str:
        """Read a file or specific lines.

        Args:
            location: File path or "file.py:45" or "file.py:30-80"
            context: Lines of context (default 50)

        Returns:
            File content
        """
        # Parse location: file.py, file.py:45, or file.py:30-80
        if ":" in location:
            file_path, line_spec = location.rsplit(":", 1)
            if "-" in line_spec:
                start, end = line_spec.split("-")
                start, end = int(start), int(end)
            else:
                line_num = int(line_spec)
                start = max(1, line_num - context // 2)
                end = line_num + context // 2
        else:
            file_path = location
            start = 1
            end = context

        # Find the file
        full_path = self.project_path / file_path
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Read and slice lines
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        # Return requested lines (1-indexed)
        result_lines = lines[start - 1 : end]
        result = "".join(result_lines)

        # Add line numbers
        output = []
        for idx, line in enumerate(result_lines, start=start):
            output.append(f"{idx:4d} | {line.rstrip()}")

        return "\n".join(output)

    def index(self, path: Optional[str] = None, force: bool = False):
        """Index a directory.

        Args:
            path: Directory to index (default: current directory)
            force: Force full reindex instead of incremental
        """
        index_path = Path(path or self.project_path)

        self.console.print(f"[cyan]Indexing {index_path}...[/cyan]")

        docs = read_directory(index_path)
        langchain_docs = to_langchain_docs(docs)
        split_docs = chunk_docs(langchain_docs)

        # Index in BM25 store
        self.bm25_store.index_documents(split_docs)

        # Try to index in vector store if available
        if self.vector_store:
            try:
                self.vector_store.index_documents(split_docs)
            except Exception as e:
                self.console.print(
                    f"[yellow]Warning: Could not index vectors ({type(e).__name__})[/yellow]"
                )

        self.console.print(f"[green]Indexed {len(split_docs)} chunks[/green]")

    def watch(self, path: Optional[str] = None, debounce: int = 5):
        """Watch for file changes and auto-index.

        Args:
            path: Directory to watch
            debounce: Seconds to wait after last change
        """
        import time
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler

        watch_path = Path(path or self.project_path)
        last_event_time = 0

        class ChangeHandler(FileSystemEventHandler):
            def on_modified(self, event):
                nonlocal last_event_time
                if event.is_directory:
                    return
                if not self._should_index(event.src_path):
                    return
                last_event_time = time.time()

            def on_created(self, event):
                if event.is_directory:
                    return
                if not self._should_index(event.src_path):
                    return
                nonlocal last_event_time
                last_event_time = time.time()

            @staticmethod
            def _should_index(path: str) -> bool:
                p = Path(path)
                # Check extension and ignored dirs
                if p.suffix not in ALLOWED_EXTENSIONS:
                    return False
                if any(ignored in p.parts for ignored in IGNORED_DIRS):
                    return False
                return True

        observer = Observer()
        observer.schedule(ChangeHandler(), str(watch_path), recursive=True)
        observer.start()

        self.console.print(f"[cyan]Watching {watch_path} (debounce: {debounce}s)[/cyan]")
        self.console.print("[dim]Press Ctrl+C to stop[/dim]")

        try:
            while True:
                now = time.time()
                if last_event_time and (now - last_event_time) >= debounce:
                    self.console.print(f"[cyan]Change detected, re-indexing...[/cyan]")
                    self.index(str(watch_path))
                    last_event_time = 0
                time.sleep(0.5)
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Watch stopped[/yellow]")
            observer.stop()

        observer.join()

    def status(self, path: Optional[str] = None):
        """Show index status."""
        num_chunks = len(self.bm25_store.corpus) if self.bm25_store.corpus else 0

        if num_chunks == 0:
            self.console.print("[yellow]No index found. Run 'greppy index' to create one.[/yellow]")
            return

        table = Table(title="Index Status")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Chunks indexed", str(num_chunks))
        table.add_row("Index directory", "./bm25_db")
        table.add_row("Vector store", "./chroma_db")

        self.console.print(table)

    def clear(self):
        """Clear all indexes."""
        import shutil

        self.console.print("[yellow]Clearing indexes...[/yellow]")
        for dir_name in ["./bm25_db", "./chroma_db"]:
            if Path(dir_name).exists():
                shutil.rmtree(dir_name)
                self.console.print(f"[green]Cleared {dir_name}[/green]")

        # Reinitialize stores
        self.bm25_store = BM25Store()
        self.vector_store = VectorStore()

    def format_results(self, results: List[dict], method: str = "search") -> str:
        """Format search results for display."""
        if not results:
            return "[yellow]No documents found.[/yellow]"

        output = f"[cyan]Retrieved {len(results)} documents ({method}):[/cyan]\n\n"

        for result in results:
            output += f"[magenta]--- Result {result['rank']} ---[/magenta]\n"
            content = result["content"]
            if len(content) > 500:
                content = content[:497].rstrip() + "..."
            output += f"{content}\n"

            if result["metadata"]:
                path = result["metadata"].get("path", "unknown")
                output += f"[dim][Source: {path}][/dim]\n"
            output += "\n"

        return output
