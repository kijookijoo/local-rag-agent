# Atlas

A lightweight local Retrieval-Augmented Generation (RAG) system that indexes a directory of files, stores embeddings in a vector database, and enables semantic search and question answering over local codebases or document collections.

---

## Overview

This project implements a full RAG pipeline from scratch for local development use. It allows you to:

- Index any local directory of files
- Chunk documents into semantically meaningful segments
- Generate embeddings using a transformer-based model
- Store and retrieve embeddings using ChromaDB
- Perform semantic search over your files
- Ask natural language questions using an LLM over retrieved context

Instead of relying on keyword search tools like grep, you can query your codebase using natural language.

---

## Architecture

### Pipeline Flow

Local Files  
→ Ingestion (directory traversal)  
→ Filtering (allowed file types + ignored directories)  
→ Conversion to LangChain Documents  
→ Chunking (RecursiveCharacterTextSplitter)  
→ File Hashing (incremental change detection)  
→ Embedding Generation  
→ Vector Storage (ChromaDB)  
→ Retrieval (semantic similarity search)  
→ LLM Response Generation (RAG agent)

---

## Core Components

### Ingestion Layer
Responsible for reading files from a directory.

- Uses `os.walk` to traverse directories
- Filters files based on:
  - allowed extensions
  - ignored directories (node_modules, .git, etc.)
- Outputs raw file content with metadata

---

### Chunking Layer
Splits documents into smaller chunks before embedding.

- Uses `RecursiveCharacterTextSplitter`
- Applies overlap between chunks to preserve context
- Converts raw documents into LangChain `Document` objects

---

### Embedding Layer
Transforms text into vector representations.

- Uses sentence-transformer model (`all-MiniLM-L6-v2`)
- Produces dense embeddings for semantic similarity search

---

### Vector Store (ChromaDB)
Handles storage and retrieval of embeddings.

- Persistent local vector database (`./chroma_db`)
- Stores:
  - embeddings
  - document text
  - metadata (file path, content hash)

#### Incremental indexing
Each file is hashed using SHA-256. If the hash has not changed, the file is skipped to avoid unnecessary re-embedding.

---

### Retrieval System
Performs semantic search over stored embeddings.

- Uses cosine similarity internally via ChromaDB
- Supports configurable top-k retrieval

---

### RAG Agent
Combines retrieved context with a language model.

- Retrieves relevant chunks from vector store
- Injects context into a structured prompt
- Generates response using ChatOpenAI

---

## Project Structure
rag-agent/
│
├── ingest.py # File traversal and reading
├── chunker.py # Text splitting logic
├── embeddings.py # Embedding model loader
├── vectorstore.py # ChromaDB + indexing logic
├── rag.py # RAG agent (LLM + retrieval)
├── main.py # CLI entry point
├── config.py # File filters and ignored directories
│
├── chroma_db/ # Persistent vector database
└── README.md

---

## How to Run

### Install dependencies

```bash
pip install -r requirements.txt

Set API key

macOS/Linux:

export OPENAI_API_KEY="your-api-key"

Windows:

setx OPENAI_API_KEY "your-api-key"

Run the application

atlas


Example Usage

Enter query: where is authentication implemented?

----------------------------------------
auth.py
def login_user(...)

----------------------------------------

Response:
Authentication logic is implemented in auth.py within the login_user function...
