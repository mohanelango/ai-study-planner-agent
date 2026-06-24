# AI Study Planner Agent

Resume-optimized AI portfolio project for an AI-assisted study planner.

Weekend 1 created the runnable local skeleton. Weekend 2 added the database foundation. Weekend 3 added auth, profile, availability, and goal setup. Weekend 4 added deterministic rule-based study plan generation and calendar APIs. Weekend 5 adds OpenAI-powered plan explanations with internal agent logging.

## Architecture

- Modular monolith backend
- Separate Celery worker processes
- FastAPI API service
- React + TypeScript frontend
- PostgreSQL primary relational database
- Docker Compose based local development

## Tech Stack

- Backend: FastAPI, Pydantic, pydantic-settings, SQLAlchemy, Alembic, Passlib, python-jose
- Frontend: React, TypeScript, Vite
- Workers: Celery, Celery Beat
- Infrastructure: PostgreSQL, Redis, Qdrant, MinIO
- Local orchestration: Docker Compose

## Weekend 1 Includes

- Backend skeleton
- Frontend skeleton
- Docker Compose infrastructure
- Health endpoint
- Celery placeholder app and health/debug task
- Central settings, logging, and exception handlers
- Placeholder docs
- Empty modular folders for future MVP features

## Weekend 2 Adds

- SQLAlchemy database foundation
- Alembic migrations
- MVP database tables:
  - `users`
  - `student_profiles`
  - `availability_windows`
  - `study_goals`
  - `subjects`
  - `topics`
  - `background_jobs`
- Repository interfaces and PostgreSQL implementations
- Unit of Work placeholder
- PostgreSQL dependency health check
- Integration tests for repositories

## Weekend 3 Adds

- Register/login APIs
- JWT-protected routes
- Bcrypt password hashing
- Current user endpoint
- Profile create/get/update APIs
- Availability create/list/delete APIs
- Goal create/list/detail/update/archive APIs
- Subject create/list APIs
- Topic create/list APIs
- Ownership checks so users can access only their own records
- Basic frontend forms for register, login, profile setup, availability setup, goal setup, subjects, and topics

## Weekend 4 Adds

- Study plan tables:
  - `study_plans`
  - `study_plan_versions`
  - `study_sessions`
  - `study_tasks`
- Deterministic rule-based planner
- Study plan generation API
- Calendar API
- Today's tasks API
- Plan version metadata API
- Basic frontend planning pages for generation, calendar, and today's tasks

## Weekend 5 Adds

- OpenAI provider abstraction
- Prompt management with file-based templates
- Agent run logging
- LLM prompt/response logging
- AI explanation for deterministic study plans
- Safe frontend explanation display

## Not Included Yet

- RAG implementation
- PDF upload or processing
- Embeddings
- Qdrant logic
- MinIO logic
- Quiz generation
- Progress tracking
- Weak-area detection
- Adaptive replanning
- AI coach
- Production AI workflows

## Setup

1. Install Docker Desktop.
2. Copy the environment file:

```bash
cp .env.example .env
```

PowerShell:

```powershell
Copy-Item .env.example .env
```

3. Start the stack:

```bash
docker compose up --build
```

4. Run database migrations:

```bash
docker compose exec backend alembic upgrade head
```

5. Check migration status:

```bash
docker compose exec backend alembic current
docker compose exec backend alembic history
```

6. Run backend tests:

```bash
docker compose exec backend python -m unittest discover -s tests
```

7. Open:

- Backend health: `http://localhost:8000/api/v1/health`
- Backend dependency health: `http://localhost:8000/api/v1/health/dependencies`
- Backend docs: `http://localhost:8000/docs`
- Frontend: `http://localhost:3000`
- MinIO console: `http://localhost:9001`

## Weekend 3 Manual API Flow

1. Register a user with `POST /api/v1/auth/register`.
2. Login with `POST /api/v1/auth/login`.
3. Use the returned Bearer token for `GET /api/v1/auth/me`.
4. Create profile with `POST /api/v1/profiles`.
5. Add availability with `POST /api/v1/availability`.
6. Create goal with `POST /api/v1/goals`.
7. Add subject with `POST /api/v1/goals/{goal_id}/subjects`.
8. Add topic with `POST /api/v1/subjects/{subject_id}/topics`.

## Weekend 4 Manual API Flow

1. Register/login.
2. Create profile.
3. Add availability.
4. Create goal.
5. Add subjects/topics.
6. Generate plan with `POST /api/v1/plans/generate`.
7. View calendar with `GET /api/v1/plans/{plan_id}/calendar`.
8. View today's tasks with `GET /api/v1/plans/{plan_id}/today`.

## Weekend 5 Manual API Flow

1. Complete the Weekend 4 flow and generate a study plan.
2. Set `OPENAI_API_KEY` in `.env`.
3. Restart the backend.
4. Generate an explanation with `POST /api/v1/plans/{plan_id}/explain`.
5. Confirm the frontend shows headline, summary, rationale, warnings, and actions.
6. Confirm raw prompts, raw responses, token usage, and email are not shown.

## Host Tooling Notes

Node.js/npm is optional for local frontend development, but it is not required when running with Docker Compose.

Python is optional on the host when running with Docker Compose.

`OPENAI_API_KEY` is required only for AI plan explanations. The rest of the app continues to work without it.

## Verification

```bash
python -m compileall backend/app backend/tests
docker compose config
docker compose up --build
docker compose exec backend alembic upgrade head
docker compose exec backend python -m unittest discover -s tests
```

Optional host frontend check if Node.js/npm are installed:

```bash
cd frontend
npm install
npm run build
```