# Architecture

AI Study Planner Agent is a resume-optimized MVP built as a modular monolith with separate Celery worker processes.

## Backend

- FastAPI API layer
- Module-owned schemas, services, repositories, and domain rules
- SQLAlchemy persistence layer
- Alembic migrations
- JWT-protected user-owned product APIs

## Planner Layer

The planning module contains a deterministic `RuleBasedPlanner` in the domain layer. It uses existing goals, topics, and availability windows to create study plans, plan versions, sessions, and tasks.

The planner domain does not import FastAPI, SQLAlchemy, Celery, OpenAI, Qdrant, or MinIO.

## Weekend 5 Explanation Layer

The agents module explains an already-generated study plan using an LLM provider abstraction.

- OpenAI calls are centralized in `app.infrastructure.llm.openai_provider`.
- Services and routes use the provider abstraction only.
- Prompt templates live outside Python service code.
- Agent runs, prompts, and responses are logged internally.
- Sanitized plan context excludes emails, password hashes, JWTs, keys, and unrelated user data.

## Weekend 6 Document Ingestion Layer

The documents module implements ingestion only:

`Upload PDF -> MinIO -> document row -> background job -> Celery worker -> PyMuPDF extraction -> text cleaning -> chunking -> document_chunks table`

Storage access is centralized behind `app.infrastructure.storage`. PDF extraction and text processing are centralized in `app.infrastructure.document_processing`.

Weekend 6 does not create embeddings, write to Qdrant, answer questions from notes, or call OpenAI for documents.

## Deferred

No embeddings, Qdrant vector search, RAG answer generation, quiz generation, progress tracking, weak-area detection, adaptive replanning, or AI coach logic is implemented yet.
