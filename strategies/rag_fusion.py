from chains.multiquery import MultiQueryGenerator
from collections import defaultdict

SIMILARITY_DIST_THRESHOLD = 1.55

class RAGFusionStrategy:
    def __init__(self, llm, retriever):
        self.llm = llm
        self.retriever = retriever
        self.generator = MultiQueryGenerator(llm)
    
    def retrieve(self, query):
        generated_queries = self.generator.chain.invoke(query)
    
        scores = defaultdict(float)
        docs = {}
        
        for q in generated_queries:
            retrieved_docs = self.retriever.vectorstore.similarity_search_with_score(
                q,
                k=5
            )
            
            for rank, (doc,score) in enumerate(retrieved_docs):
                if score > SIMILARITY_DIST_THRESHOLD:
                    continue
                key = (
                    doc.metadata["path"] + doc.page_content
                )
                
                docs[key] = doc
                # smoothing constant to normalize the contribution of rank on the scores
                scores[key] += 1 / (rank + 60)
        res = []
        for key,score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            res.append(docs[key])
        
        return res  
        