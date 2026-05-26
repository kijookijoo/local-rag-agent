from pathlib import Path

import bm25s
from langchain_core.documents import Document


class BM25Store:
    def __init__(self, index_dir: str = "./bm25_db"):
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.index = bm25s.BM25()
        self.corpus = []
        self._load()

    def _load(self):
        if not self.index_dir.exists():
            return

        try:
            self.index = bm25s.BM25.load(str(self.index_dir), load_corpus=True)
            self.corpus = self.index.corpus or []
        except FileNotFoundError:
            self.index = bm25s.BM25()
            self.corpus = []

    def index_documents(self, chunk_docs):
        self.corpus = [
            {
                "page_content": doc.page_content,
                "metadata": dict(doc.metadata),
            }
            for doc in chunk_docs
        ]

        tokenized_corpus = bm25s.tokenize(
            [item["page_content"] for item in self.corpus],
            return_ids=False,
        )
        self.index = bm25s.BM25()
        self.index.index(tokenized_corpus, create_empty_token=True)
        self.index.save(str(self.index_dir), corpus=self.corpus)

    def search(self, query: str, k: int = 20):
        if not self.corpus:
            return []

        tokenized_query = bm25s.tokenize(query, return_ids=False)
        results = self.index.retrieve(
            tokenized_query,
            corpus=self.corpus,
            k=k,
            sorted=True,
        )

        docs = []
        for item in results.documents[0]:
            docs.append(
                Document(
                    page_content=item["page_content"],
                    metadata=item["metadata"],
                )
            )
        return docs

    def as_retriever(self, k: int = 20):
        store = self

        class BM25Retriever:
            def invoke(self, query: str):
                return store.search(query, k=k)

        return BM25Retriever()
