from collections import defaultdict

from ..chains.multiquery import MultiQueryGenerator

SIMILARITY_DIST_THRESHOLD = 1.55


class RAGFusionStrategy:
    def __init__(self, llm, dense_retriever, bm25_retriever=None):
        self.llm = llm
        self.dense_retriever = dense_retriever
        self.bm25_retriever = bm25_retriever
        self.generator = MultiQueryGenerator(llm)

    def retrieve(self, query):
        generated_queries = self.generator.chain.invoke(query)

        scores = defaultdict(float)
        docs = {}

        for q in generated_queries:
            retrieved_docs = self.dense_retriever.vectorstore.similarity_search_with_score(q, k=5)
            for rank, (doc, score) in enumerate(retrieved_docs):
                if score > SIMILARITY_DIST_THRESHOLD:
                    continue
                key = doc.metadata["path"] + doc.page_content
                docs[key] = doc
                scores[key] += 1 / (rank + 60)

            if self.bm25_retriever is not None:
                bm25_docs = self.bm25_retriever.invoke(q)
                for rank, doc in enumerate(bm25_docs):
                    key = doc.metadata["path"] + doc.page_content
                    docs[key] = doc
                    scores[key] += 1 / (rank + 60)

        res = []
        for key, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            res.append(docs[key])
        return res
