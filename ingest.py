from pathlib import Path
from config import ALLOWED_EXTENSIONS, IGNORED_DIRS
from langchain_core.documents import Document
import os
def read_directory(directory: Path):
    """
    Traverse the directory given the path to it. Read the contents of the files in that directory, and return
    the metadata (path and content) as a dictionary
    """
    documents = []
    for root,dirs,files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        
        for name in files:
            path = Path(root) / name
            if path.suffix not in ALLOWED_EXTENSIONS:
                continue
            try:
                content = path.read_text()
                documents.append(
                    {
                        "path":str(path),
                        "content":content
                    }
                )
            except:
                pass
    return documents

def to_langchain_docs(documents):
    res = []
    for d in documents:
        res.append(
            Document(
                page_content = d["content"],
                metadatas = {"path": d["path"]}
            )
        )

    return res