## Architecture Overview

The AI-POC pipeline retrieves relevant internal content and augments the LLM’s response using ChromaDB-stored KB/SOP embeddings.

```mermaid
flowchart TD
    U["Users"]
    W["OpenWebUI<br/>(Chat Client)"]
    R["RAG API<br/>Query Orchestration<br/>Prompt Builder"]
    C["ChromaDB<br/>(Vector Store)"]
    O["Ollama<br/>(Local LLM)"]
    A["Final Answer"]

    U -->|"HTTPS"| W
    W -->|"RAG Tool Call"| R
    R -->|"Retrieve relevant chunks"| C
    C -->|"Context + metadata"| R
    R -->|"Grounded prompt"| O
    O -->|"Generated response"| R
    R --> A
    A --> W
    W --> U

    classDef user fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef service fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef model fill:#ede9fe,stroke:#7c3aed,color:#3b0764
    classDef storage fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef output fill:#f3f4f6,stroke:#6b7280,color:#111827

    class U,W user
    class R service
    class C storage
    class O model
    class A output
```

---

## Data Ingestion & Indexing Workflow

Internal KB & SOP directories on the Windows file server are mounted into the Linux host and processed by the indexer container:

```mermaid
flowchart TD
    F["CIFS File Shares<br/>//fileshare/.../KB<br/>//fileshare/.../SOP"]
    M["Linux Host Mounts<br/>/mnt/KB<br/>/mnt/SOPs"]
    I["kb-indexer Container<br/>Reads PDFs / DOCX<br/>Extracts text<br/>Chunks documents<br/>Pushes embeddings"]
    C["ChromaDB Collection<br/>enterprise_collections"]

    F --> M
    M --> I
    I --> C

    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef host fill:#f3f4f6,stroke:#6b7280,color:#111827
    classDef service fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef storage fill:#dcfce7,stroke:#16a34a,color:#14532d

    class F source
    class M host
    class I service
    class C storage
```

This ensures all documentation is searchable and query-ready.

---

## RAG Query Flow (Step-by-Step)

1. User asks a question in OpenWebUI.

2. OpenWebUI’s RAG tool sends the question → RAG API.

3. RAG API queries ChromaDB (collection: enterprise_collections) to retrieve the top-K relevant chunks.

4. RAG API inserts those chunks into a structured prompt.

5. RAG API sends the prompt to Ollama, which performs LLM inference on-prem.

6. The LLM generates the final answer with context and citations.

7. OpenWebUI displays the answer to the user.

All retrieval and inference operations occur internally.

---

## Core Components

1. OpenWebUI

    * Main chat interface for IT and researchers

    * Supports RAG tool integration

    * Hosted locally and isolated from external networks

2. RAG API

    * Python/FastAPI microservice
    * Handles:
        * retrieval -> propmpt building -> LLM inference
        * formatting prompt templates
        * managing context windows

3. chromaDB
    * Vector database storing embeddings
    * Collection: enterprise_collections
    * Accessible only on internal Docker networks

4. Ollama
    * Local LLM runtime (GPU-enabled)
    * Supports models such as:
        * llama2:7b
        * pi4-reasoning:14b
    * Encsures data never leaves the internal environment

5. kb-indexer
    * Scans mounted KB/SOP directories
    * Converts PDF/DOCX -> text
    * Pushes to ChromaDB

---

# Security & Isolation

Fully on-prem; no external APIs

CIFS mounts set to read-only from Windows file server

Docker network isolation prevents cross-container exposure
