# AI Workflows

Weekend 5 adds one AI workflow: study plan explanation.

## Study Plan Explanation

- The deterministic planner remains the source of truth.
- The LLM receives sanitized plan context only.
- The LLM must not create, change, reorder, or invent schedule items.
- Agent runs, prompts, and responses are logged internally.
- Raw prompts and raw responses are not exposed through standard APIs or the frontend.

## Not Implemented Yet

- RAG
- PDF upload
- embeddings
- retrieval
- quiz generation
- progress tracking
- weak-area detection
- adaptive replanning
- AI coach
