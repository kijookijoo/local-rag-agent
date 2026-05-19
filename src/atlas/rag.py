class RAGAgent:
    def __init__(self, strategy, llm):
        self.strategy = strategy
        self.llm = llm

    def ask(self, query, chat_history=None):
        docs = self.strategy.retrieve(query)
        context = "\n".join([d.page_content for d in docs])

        history_text = ""
        if chat_history:
            turns = []
            for turn in chat_history:
                turns.append(f"User: {turn['user']}")
                turns.append(f"Assistant: {turn['assistant']}")
            history_text = "\n".join(turns)

        prompt = f"""
You are a RAG agent. Answer using the retrieved context first.

Conversation history:
{history_text if history_text else "None"}

Retrieved context:
{context if context else "None"}

Question:
{query}
"""

        return self.llm.invoke(prompt).content
