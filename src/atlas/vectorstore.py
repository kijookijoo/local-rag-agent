from collections import defaultdict

from langchain_chroma import Chroma

from .index_state import content_hash
from .embeddings import load_embedding_model


class VectorStore:
    def __init__(self, db_dir="./chroma_db"):
        self.embedding_model = load_embedding_model()
        self.db = Chroma(
            persist_directory=db_dir,
            embedding_function=self.embedding_model,
        )

    def index_documents(self, chunk_docs):
        by_file = defaultdict(list)
        for doc in chunk_docs:
            by_file[doc.metadata["path"]].append(doc)

        for path, docs in by_file.items():
            full_text = "".join(d.page_content for d in docs)
            new_hash = content_hash(full_text)
            prev = self.db.get(where={"path": path})

            if len(prev["ids"]) > 0:
                prev_hash = prev["metadatas"][0].get("hash")
                if prev_hash == new_hash:
                    continue
                self.db.delete(where={"path": path})

            for d in docs:
                d.metadata["hash"] = new_hash

            self.db.add_documents(docs)

    def as_retriever(self, k=20):
        return self.db.as_retriever(search_kwargs={"k": k})
