from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

class BasicChain:
    def __init__(self, llm, retriever):
        # the template fills in the variables and then returned the completed string
        prompt = ChatPromptTemplate.from_template(
            """
            Answer the question based only on the context below.

            Context:
            {context}

            Question:
            {question}
            """
        )
        
        # query -> retriever -> generation
        self.chain = (
            {"context": retriever,
             "question": RunnablePassthrough()} 
            | prompt
            | llm
            | StrOutputParser()            
        )
        
    
