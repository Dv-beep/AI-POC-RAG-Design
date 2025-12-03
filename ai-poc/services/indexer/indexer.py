"""
KB Indexer

Scans one or more knowledge base root directories, reads supported files
(.txt, .md, .pdf, .docx), chunks them, and sends the content to a RAG API
/ingest endpoint for storage in a vector database (e.g. ChromaDB).
"""


import os
import hashlib
import json
import requests
from datetime import datetime, timezone
from typing import List, Dict

from pypdf import PdfReader
from docx import Document

# Environment variables (set in docker-compose)
KB_ROOTS_ENV = os.environ.get("KB_ROOTS", "/kb/knowledgebase,/kb/sops")
RAG_API_URL = os.environ.get("RAG_API_URL", "http://rag-api:9000")

# Comma-separated list of roots inside the container
KB_ROOTS = [p.strip() for p in KB_ROOTS_ENV.split(",") if p.strip()]

# Simple file extensions
TEXT_EXTENSIONS = {".txt", ".md", ".markdown", ".log"}
PDF_EXTENSIONS = {".pdf"}
DOCX_EXTENSIONS = {".docx"}


def log(msg: str) -> None:
    print(f"[INDEXER] {msg}", flush=True)


def file_sha256(path: str, chunk_size: int = 8192) -> str:
    """Return SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk_size), b""):
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def iso_utc_from_mtime(path: str) -> str:
    """Return file mtime as ISO8601 UTC string."""
    ts = os.stat(path).st_mtime
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")


def chunk_text(text: str, max_chars: int = 1500) -> List[str]:
    """Naive chunker: split text into ~max_chars segments on newline/space where possible."""
    text = text.strip()
    if not text:
        return []

    chunks = []
    start = 0
    length = len(text)

    while start < length:
        end = min(start + max_chars, length)
        cut = end

        # Try to cut on newline or space near the end
        newline_pos = text.rfind("\n", start, end)
        space_pos = text.rfind(" ", start, end)

        if newline_pos != -1:
            cut = newline_pos + 1
        elif space_pos != -1:
            cut = space_pos + 1

        chunk = text[start:cut].strip()
        if chunk:
            chunks.append(chunk)

        start = cut

    return chunks


def read_text_file(path: str) -> str:
    """Read a plain text file as UTF-8 (best effort)."""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def read_pdf_file(path: str) -> str:
    """Extract text from a PDF using pypdf."""
    try:
        reader = PdfReader(path)
        texts = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            texts.append(page_text)
        return "\n".join(texts)
    except Exception as e:
        log(f"Error reading PDF {path}: {e}")
        return ""


def read_docx_file(path: str) -> str:
    """Extract text from a DOCX using python-docx."""
    try:
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception as e:
        log(f"Error reading DOCX {path}: {e}")
        return ""


def should_index_file(path: str) -> bool:
    """Decide if a file should be indexed based on extension."""
    if not os.path.isfile(path):
        return False

    name = os.path.basename(path)
    if name.startswith("."):
        return False

    _, ext = os.path.splitext(name)
    ext = ext.lower()

    if ext in TEXT_EXTENSIONS | PDF_EXTENSIONS | DOCX_EXTENSIONS:
        return True

    return False


def read_file_as_text(path: str) -> str:
    """Route to the proper reader by extension."""
    _, ext = os.path.splitext(path)
    ext = ext.lower()

    if ext in TEXT_EXTENSIONS:
        return read_text_file(path)
    elif ext in PDF_EXTENSIONS:
        return read_pdf_file(path)
    elif ext in DOCX_EXTENSIONS:
        return read_docx_file(path)
    else:
        # Fallback: treat as text
        return read_text_file(path)


def build_document_id(root_label: str, full_path: str, root_path: str) -> str:
    """
    Build a stable document_id, e.g.:
      root_label = "sops"
      full_path  = "/kb/sops/chromadb_canary.txt"
      root_path  = "/kb/sops"
    => document_id = "sops/chromadb_canary.txt"
    """
    rel_path = os.path.relpath(full_path, start=root_path)
    rel_path = rel_path.replace(os.sep, "/")
    return f"{root_label}/{rel_path}"


def ingest_file(root_label: str, root_path: str, full_path: str) -> None:
    """Read, chunk, and send a single file to the RAG API /ingest endpoint."""
    if not should_index_file(full_path):
        log(f"Skipping unsupported or non-text file: {full_path}")
        return

    name = os.path.basename(full_path)
    _, ext = os.path.splitext(name)
    ext = ext.lower()

    log(f"Indexing file: {full_path}")

    # Build document_id (stable across runs)
    document_id = build_document_id(root_label, full_path, root_path)

    # Hash + last_modified
    doc_hash = file_sha256(full_path)
    last_modified = iso_utc_from_mtime(full_path)

    # Read & chunk
    raw_text = read_file_as_text(full_path)
    text_chunks = chunk_text(raw_text, max_chars=1500)

    if not text_chunks:
        log(f"No content to index in file: {full_path}")
        return

    chunks: List[Dict] = []
    total_chunks = len(text_chunks)

    for idx, chunk_text_block in enumerate(text_chunks):
        chunk_id = f"{document_id}#chunk-{idx}"

        chunks.append(
            {
                "id": chunk_id,
                "text": chunk_text_block,
                "metadata": {
                    "path": name,
                    "source": root_label,
                    "file_type": ext.lstrip("."),
                    "chunk_index": idx,
                    "chunk_count": total_chunks,
                },
            }
        )

    payload = {
        "document_id": document_id,
        "doc_hash": doc_hash,
        "last_modified": last_modified,
        "chunks": chunks,
    }

    try:
        resp = requests.post(
            f"{RAG_API_URL}/ingest",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=120,
        )
        log(f"Ingest response for {document_id}: {resp.status_code} {resp.text}")
    except Exception as e:
        log(f"Error ingesting {document_id}: {e}")


def index_root(root_path: str) -> None:
    """
    Walk a single root, e.g. /kb/knowledgebase or /kb/sops.
    The root_label is derived from the final path segment ("knowledgebase", "sops").
    """
    root_label = os.path.basename(root_path.rstrip("/"))
    if not os.path.isdir(root_path):
        log(f"Root path does not exist or is not a directory: {root_path}")
        return

    log(f"Scanning root '{root_label}' at {root_path}")

    for dirpath, dirnames, filenames in os.walk(root_path):
        # Skip hidden dirs
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]

        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            ingest_file(root_label, root_path, full_path)


def main() -> None:
    log(f"KB_ROOTS: {KB_ROOTS}")
    log(f"RAG_API_URL: {RAG_API_URL}")

    for root in KB_ROOTS:
        index_root(root)

    log("Indexing completed.")


if __name__ == "__main__":
    main()


