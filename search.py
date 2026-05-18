def search(vectorstore, query):
    retriever = vectorstore.as_retriever()
    results = retriever.invoke(query)
    
    for r in results:
        print(r.metadata["path"])
        print(r.page_content)
        print("-" * 50)