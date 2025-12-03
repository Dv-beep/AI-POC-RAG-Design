# AI-POC-RAG-Design

Overview

The AI-POC implements a Retrieval-Augmented Generation (RAG) pipeline that enables internal knowledge retrieval from TLI KB/SOP repositories while keeping all data on-prem and behind the firewall. The system uses a modular containerized architecture built around OpenWebUI, a custom RAG API service, ChromaDB as the vector store, and Ollama as the local LLM engine.

The design allows internal users to query organizational knowledge, while ensuring that all documents, embeddings, and LLM inference stay inside the controlled environment.
