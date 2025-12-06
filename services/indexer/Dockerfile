FROM python:3.11-slim

WORKDIR /app

# System deps (for pip + some parsing libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
  && rm -rf /var/lib/apt/lists/*

# Python deps for Chroma client + document parsing + HTTP ingestion
RUN pip install --no-cache-dir \
    chromadb \
    pypdf \
    python-docx \
    requests \
    pandas \
    openpyxl

COPY indexer.py /app/indexer.py

CMD ["python", "indexer.py"]

