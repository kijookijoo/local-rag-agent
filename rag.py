class RAGAgent:
    def __init__(self, strategy, llm):
        self.strategy = strategy
        self.llm = llm
    
    def ask(self, query):
        docs = self.strategy.retrieve(query)
        
        context = "\n".join([d.page_content for d in docs])

        prompt = f"""
        You are a RAG agent. Answer prioritizing the context below.
        
        context:{context}
        
        Question={query}
        """
        
        return self.llm.invoke(prompt).content
        