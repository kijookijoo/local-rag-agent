from ingest import read_directory
from chunker import chunk_docs,to_langchain_docs
from vectorstore import build_vectorstore
from pathlib import Path

def main():
    directory = Path(input("Enter directory: "))
    docs = read_directory(directory)
    langchain_docs = to_langchain_docs(docs)
    split_docs = chunk_docs(langchain_docs)
    chromadb = build_vectorstore(split_docs)
    print("Indexing done!")

main()
    
    
    
    
    