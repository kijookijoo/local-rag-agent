import os

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
if hf_token:
    os.environ.setdefault("HUGGINGFACEHUB_API_TOKEN", hf_token)
    os.environ.setdefault("HF_TOKEN", hf_token)


def load_embedding_model():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"token": hf_token} if hf_token else None,
    )
