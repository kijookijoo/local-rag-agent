import os
import ssl
import logging

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings

logger = logging.getLogger(__name__)
load_dotenv()

hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
if hf_token:
    os.environ.setdefault("HUGGINGFACEHUB_API_TOKEN", hf_token)
    os.environ.setdefault("HF_TOKEN", hf_token)


def load_embedding_model():
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    ssl._create_default_https_context = ssl._create_unverified_context

    try:
        return HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"token": hf_token} if hf_token else None,
            cache_folder=os.path.expanduser("~/.cache/huggingface"),
        )
    except Exception as e:
        logger.warning(f"Failed to load embedding model: {e}")
        logger.warning("Embeddings will not be available for semantic search")
        raise
