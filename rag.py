
class RAGAgent:
    def __init__(self, vectorstore, llm):
        self.vectorstore = vectorstore 
        self.llm = llm
    
    def ask(self, query):
        retrival = self.vectorstore.search(query)
        context = "".join([doc for doc in retrival])

        prompt = f"""
        You are a RAG agent. Answer prioritizing the context below.
        
        context:{context}
        
        Question={query}
        """
        
        return self.llm.invoke(prompt)
        