from ingest import read_directory
from chunker import chunk_docs
from ingest import to_langchain_docs
from vectorstore import VectorStore
from rag import RAGAgent
from pathlib import Path
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import chains
import os
import getpass

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")    

def main():
    cwd = Path(os.getcwd())
    docs = read_directory(cwd)
    langchain_docs = to_langchain_docs(docs)
    split_docs = chunk_docs(langchain_docs)
    vectorstore = VectorStore()
    vectorstore.index_documents(split_docs)
    print("Indexing done!")
    
    # ChatOpenAI automatically picks up OPENAI_API_KEY from .env
    agent = RAGAgent(vectorstore, 
                     ChatOpenAI(
                         model_name= os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini"), 
                         temperature=0
                         )
                     )
    
    while True:
        query = input("Enter query :")
        result = vectorstore.search(query)
        
        if result:
            print("Retrieved Documents:")
            print("\n")
            
        for doc in result:
            print(doc.page_content)
            print("\n")
            print("-" * 20)
            
        response = agent.ask(query)
        print("-" * 20)
        print(response)
        
# RAG Chain
# Retrieval -> fed into context window along with prompt -> generation
if __name__ == "__main__":
    main()
    
    
    
    
    