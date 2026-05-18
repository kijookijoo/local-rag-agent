from embeddings import load_embedding_model
from langchain_community.vectorstores import Chroma

def build_vectorstore(split_docs):
    embedding_model = load_embedding_model()
    vectorstore = Chroma.from_documents(
        documents=split_docs,
        embedding=embedding_model,
        persist_directory="./chroma_db"
    )
    return vectorstore
    

    