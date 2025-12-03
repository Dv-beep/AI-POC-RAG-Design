## KB Indexer

The `services/indexer/` service scans mounted knowledge base and SOP directories,
extracts text from `.txt`, `.md`, `.pdf`, and `.docx` files, chunks them,
and sends them to the RAG API’s `/ingest` endpoint.

Environment variables:
- `KB_ROOTS` – Comma-separated list of root folders inside the container *(default: `/kb/knowledgebase,/kb/sops`)*
- `RAG_API_URL` – Base URL for the RAG API
 *(default: `http://rag-api:9000`)*