# API Contract

All product endpoints return:

```json
{
  "success": true,
  "message": "...",
  "data": {}
}
```

Errors use the existing `AppException` response format.

## Health

- `GET /api/v1/health`
- `GET /api/v1/health/dependencies`

OpenAI health returns `configured` or `not_configured` only. It does not make a live API call.

## Auth/Profile/Goals

Weekend 3 includes register/login, current user, profile, availability, goals, subjects, and topics endpoints.

## Planning

Authenticated endpoints:

- `POST /api/v1/plans/generate`
- `GET /api/v1/plans/{plan_id}`
- `GET /api/v1/plans/{plan_id}/calendar`
- `GET /api/v1/plans/{plan_id}/today`
- `GET /api/v1/plans/{plan_id}/versions`
- `GET /api/v1/plans/{plan_id}/versions/{version_id}`

## Weekend 5 Explanation

- `POST /api/v1/plans/{plan_id}/explain`

The endpoint explains an existing deterministic plan. It does not create, modify, or re-order schedule sessions/tasks.

The response does not expose raw prompts, raw LLM responses, token usage, user email, or secrets.

## Weekend 6 Documents

Authenticated endpoints:

- `POST /api/v1/documents/upload`
- `GET /api/v1/documents`
- `GET /api/v1/documents/{document_id}`
- `GET /api/v1/documents/{document_id}/status`
- `GET /api/v1/documents/{document_id}/chunks`
- `DELETE /api/v1/documents/{document_id}`
- `GET /api/v1/jobs/{job_id}`

Document responses do not expose `storage_bucket` or `storage_key`. Chunk text is returned only to the owning authenticated user for Weekend 6 debugging.

No ask-from-notes, vector search, quiz, progress, or adaptive replanning endpoints are implemented yet.
