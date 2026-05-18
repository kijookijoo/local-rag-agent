from ingest import read_directory
from chunker import chunk_docs,to_langchain_docs
from vectorstore import build_vectorstore
from pathlib import Path
from search import search

def main():
    directory = Path(input("Enter directory: "))
    docs = read_directory(directory)
    langchain_docs = to_langchain_docs(docs)
    split_docs = chunk_docs(langchain_docs)
    vectorstore = build_vectorstore(split_docs)
    print("Indexing done!")
    query = input("Enter query :")
    search(vectorstore, query)
    
if __name__ == "__main__":
    main()
    
    
    
    
    