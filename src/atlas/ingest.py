from pathlib import Path
from langchain_core.documents import Document
import os

from .config import ALLOWED_EXTENSIONS, IGNORED_DIRS


def read_directory(directory: Path):
    documents = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for name in files:
            path = Path(root) / name
            if path.suffix not in ALLOWED_EXTENSIONS:
                continue
            try:
                content = path.read_text()
                documents.append({"path": str(path), "content": content})
            except Exception:
                pass
    return documents


def to_langchain_docs(documents):
    res = []
    for d in documents:
        res.append(Document(page_content=d["content"], metadata={"path": d["path"]}))
    return res
