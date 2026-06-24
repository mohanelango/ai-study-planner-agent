# Database Schema

Weekend 5 adds internal agent and LLM logging tables on top of the deterministic planning foundation.

Implemented foundation tables:

- `users`
- `student_profiles`
- `availability_windows`
- `study_goals`
- `subjects`
- `topics`
- `background_jobs`

Implemented planning tables:

- `study_plans`
- `study_plan_versions`
- `study_sessions`
- `study_tasks`

Implemented agent logging tables:

- `agent_runs`
- `llm_prompts`
- `llm_responses`

Raw prompts and raw responses are internal only and are not exposed by normal APIs.

Not implemented yet:

- documents / RAG tables
- embeddings
- retrieval queries/chunks
- quizzes
- progress tables
- weak-area tables
- adaptive replanning tables
