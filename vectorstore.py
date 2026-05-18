from embeddings import load_embedding_model
from collections import defaultdict
from langchain_community.vectorstores import Chroma
import hashlib

class VectorStore:
    def __init__(self, db_dir="./chroma_db"):
        self.embedding_model = load_embedding_model()
        self.db = Chroma(
            persist_directory=db_dir,
            embedding_function=self.embedding_model
        )
    
    def hash(self,content):
        return hashlib.sha256(content.encode("utf-8")).hexdigest()
    
    def index_documents(self,chunk_docs):
        # gather fragmented chunks that come from the same document 
        by_file = defaultdict(list)
        for doc in chunk_docs:
            path = doc.metadata["path"] 
            by_file[path].append(doc)
            
        
        for path,docs in by_file.items():
            full_text = "".join(d.page_content for d in docs)
            newHash = self.hash(full_text)
            prev = self.db.get(where={"path":path})
            
            if len(prev["ids"]) > 0:
                prevHash = prev["metadatas"][0].get("hash")
                # prune early if there are no differences
                if prevHash == newHash:
                    continue
                
                # changes detected
                # delete all chunks associated with the older version
                self.db.delete(where={"path":path})
            
            for d in docs:
                d.metadata["hash"] = newHash
            
            self.db.add_documents(docs)
            self.db.persist()
    
    def search(self, query, k=5):
        retriever = self.db.as_retriever(search_kwargs={"k":k})
        return retriever.invoke(query)
        
            