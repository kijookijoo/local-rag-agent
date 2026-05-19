from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


class MultiQueryGenerator:
    def __init__(self, llm):
        prompt = ChatPromptTemplate.from_template(
            """
            You are a helpful assistant that generates multiple semantic search queries.

            Generate 4 alternative search queries related to:

            {question}

            Return only the queries, one per line.
            """
        )

        self.chain = prompt | llm | StrOutputParser() | (lambda x: x.split("\n"))
