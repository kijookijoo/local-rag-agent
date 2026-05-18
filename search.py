from vectorstore import build_vectorstore

def search(vectorstore, query):
    retriever = vectorstore.as_retriever(search_kwargs={"k":2})
    results = retriever.invoke(query)
    
    for r in results:
        print(r.metadata["path"])
        print(r.page_content)
        print("-" * 50)

