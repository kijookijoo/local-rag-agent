from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def to_langchain_docs(documents):
    docs = []
    for doc in documents:
        docs.append(
            Document(
                page_content=doc["content"],
                metadata={"path":doc["path"]}
            )
        )
    return docs

def chunk_docs(langchain_documents):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
    split_docs = splitter.split_documents(langchain_documents)
    return split_docs




    