from ingest import read_directory
from chunker import chunk_docs
from ingest import to_langchain_docs
from vectorstore import VectorStore
from pathlib import Path
import os

def index_run():
    cwd = Path(os.getcwd())
    docs = read_directory(cwd)
    langchain_docs = to_langchain_docs(docs)
    split_docs = chunk_docs(langchain_docs)
    vectorstore = VectorStore()
    vectorstore.index_documents(split_docs)
    print("Indexing done!")
