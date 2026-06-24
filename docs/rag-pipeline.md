# RAG Pipeline

Weekend 6 implements ingestion only. The RAG pipeline is not complete yet.

Current flow:

`Upload PDF -> MinIO -> document row -> background job -> Celery worker -> PyMuPDF extraction -> text cleaning -> chunking -> document_chunks table`

## Not Implemented Yet

- embeddings
- Qdrant vector storage
- vector search
- retrieval queries
- ask-from-notes answer generation

Embeddings and Qdrant are planned for Weekend 7. Ask-from-notes is planned for Weekend 8.
