from rag import RAGAgent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from strategies.rag_fusion import RAGFusionStrategy
from vectorstore import VectorStore
from rich.console import Console
from rich.prompt import Prompt
from rich.text import Text
import getpass
import os
   
load_dotenv()

def chat_run():
    console = Console()
    if not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ") 
    
    llm = ChatOpenAI(
        model_name= os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini"), 
        temperature=0
    )
    
    vectorstore = VectorStore()
    retriever = vectorstore.as_retriever(k=4)
    strategy = RAGFusionStrategy(llm, retriever)
    
    # ChatOpenAI automatically picks up OPENAI_API_KEY from .env    
    agent = RAGAgent(strategy, llm)
    
    while True:
        query = input("\nYou: ")
        if (query.lower() in {"exit", "quit"}):
            break
        
        retrievals = retriever.invoke(query)
        if retrievals:
            console.print("Retrieved Documents:")
            console.print("\n")
            
        for doc in retrievals:
            console.print(doc.page_content)
            console.print("\n")
            console.print("-" * 20)
            
        response = agent.ask(query)
        console.print("-" * 20)
        console.print(response)
        
    
    
    
    