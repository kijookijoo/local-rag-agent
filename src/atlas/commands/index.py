import os
from pathlib import Path

from rich.console import Console

from ..atlas_banner import print_atlas_banner
from ..bm25store import BM25Store
from ..chunker import chunk_docs
from ..ingest import read_directory, to_langchain_docs
from ..vectorstore import VectorStore


def index_run(show_banner: bool = True):
    console = Console()
    if show_banner:
        print_atlas_banner(console)
    cwd = Path(os.getcwd())
    docs = read_directory(cwd)
    langchain_docs = to_langchain_docs(docs)
    split_docs = chunk_docs(langchain_docs)
    vectorstore = VectorStore()
    vectorstore.index_documents(split_docs)
    bm25store = BM25Store()
    bm25store.index_documents(split_docs)
    console.print("[bold green]Indexing done![/bold green]")
