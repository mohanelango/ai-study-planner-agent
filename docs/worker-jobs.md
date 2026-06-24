# Worker Jobs

Weekend 6 adds one business worker job for document ingestion.

## Queues

- `default`: health/debug task
- `documents`: PDF processing task

## Document Processing Task

`documents.process_uploaded_document(document_id, background_job_id)`:

1. Marks the document/job as processing.
2. Downloads the PDF from MinIO.
3. Extracts text with PyMuPDF.
4. Cleans text.
5. Splits text into character-based chunks.
6. Deletes existing chunks for idempotency.
7. Stores chunks in PostgreSQL.
8. Marks the document/job as processed or failed.

No embeddings, Qdrant writes, RAG answering, or OpenAI document workflows are implemented yet.
