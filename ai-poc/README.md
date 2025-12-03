## RAG API (FastAPI + Chroma)

The RAG backend exposes two primary endpoints:

`POST /ingest`
- Called by the indexer. 
- Accepts pre-chunked documents
- Performs versioning based on `doc_hash`
- Replaces outdated chunks safely

- `POST /query`
- Called by the OpenWebUI tool server
- Runs a semantic search against ChromaDB
- Returns top-k chunks with metadata (path, index, version , last_modified)

**Environment variables:**
- `CHROMA_HOST` *(default: `server`)*
- `CHROMA_PORT` *(default: `8000`)*
- `COLLECTION_NAME` *(default: `enterprise_collection` or `kb_documents`)*

---

## Full Architecture

For diagrams and process flows, see:

- [docs/architecture-overview.md](https://github.com/Dv-beep/ai-platform-poc/blob/main/docs/architecture-overview.md)
- [docs/rag-sequence-diagram.md](https://github.com/Dv-beep/ai-platform-poc/blob/main/docs/rag-sequence-diagram.md)
- [docs/screenshots/](https://github.com/Dv-beep/ai-platform-poc/tree/main/docs/screenshots)