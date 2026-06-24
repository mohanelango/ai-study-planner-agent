import json
from datetime import datetime, timezone
from uuid import UUID

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config.settings import settings
from app.infrastructure.llm.base import LLMProvider, LLMRequest
from app.infrastructure.llm.exceptions import LLMResponseValidationError
from app.infrastructure.llm.factory import get_llm_provider
from app.modules.agents.infrastructure_models import AgentRun, LLMPrompt, LLMResponse
from app.modules.agents.repositories.postgres_repository import PostgresAgentRunRepository, PostgresLLMPromptRepository, PostgresLLMResponseRepository
from app.modules.agents.schemas.responses import StudyPlanExplanationPayload, StudyPlanExplanationResponse
from app.modules.agents.services.prompt_renderer import PromptRenderer
from app.modules.goals.repositories.postgres_repository import PostgresStudyGoalRepository, PostgresSubjectRepository, PostgresTopicRepository
from app.modules.planning.exceptions import PlanNotFoundError, PlanVersionNotFoundError
from app.modules.planning.repositories.postgres_repository import PostgresStudyPlanRepository, PostgresStudyPlanVersionRepository, PostgresStudySessionRepository, PostgresStudyTaskRepository


class StudyPlanExplanationService:
    def __init__(self, session: Session, llm_provider: LLMProvider | None = None, prompt_renderer: PromptRenderer | None = None) -> None:
        self.session = session
        self.llm_provider = llm_provider
        self.prompt_renderer = prompt_renderer or PromptRenderer()
        self.agent_runs = PostgresAgentRunRepository(session)
        self.prompts = PostgresLLMPromptRepository(session)
        self.responses = PostgresLLMResponseRepository(session)
        self.plans = PostgresStudyPlanRepository(session)
        self.versions = PostgresStudyPlanVersionRepository(session)
        self.sessions = PostgresStudySessionRepository(session)
        self.tasks = PostgresStudyTaskRepository(session)
        self.goals = PostgresStudyGoalRepository(session)
        self.subjects = PostgresSubjectRepository(session)
        self.topics = PostgresTopicRepository(session)

    def explain(self, user_id: UUID, plan_id: UUID, version_id: UUID | None = None) -> StudyPlanExplanationResponse:
        plan = self.plans.get_by_id(plan_id)
        if plan is None or plan.user_id != user_id or plan.status == "archived":
            raise PlanNotFoundError()

        version = self.versions.get_by_id(version_id) if version_id else self.versions.get_active_by_plan_id(plan.id)
        if version is None or version.study_plan_id != plan.id or version.user_id != user_id:
            raise PlanVersionNotFoundError()

        context = self._build_sanitized_context(user_id, plan.id, version.id)
        prompt_text = self.prompt_renderer.render("study_plan_explanation.md", {"PLAN_CONTEXT": json.dumps(context, default=str, indent=2)})
        system_prompt = "Return valid JSON only. Explain the deterministic plan without changing it."

        agent_run = self.agent_runs.add(
            AgentRun(
                user_id=user_id,
                run_type="study_plan_explanation",
                entity_type="study_plan",
                entity_id=plan.id,
                status="started",
                input_summary=f"Explain plan {plan.id} version {version.id}",
                started_at=datetime.now(timezone.utc),
            )
        )
        llm_prompt = self.prompts.add(
            LLMPrompt(
                agent_run_id=agent_run.id,
                provider="openai",
                model=settings.OPENAI_MODEL,
                prompt_type="study_plan_explanation",
                system_prompt=system_prompt,
                user_prompt=prompt_text,
                prompt_version="v1",
            )
        )
        self.session.commit()

        try:
            provider = self.llm_provider or get_llm_provider()
            llm_response = provider.generate_json(LLMRequest(system_prompt=system_prompt, user_prompt=prompt_text, temperature=0.2))
            payload = StudyPlanExplanationPayload.model_validate(llm_response.parsed_json)

            self.responses.attach_response(
                LLMResponse(
                    agent_run_id=agent_run.id,
                    llm_prompt_id=llm_prompt.id,
                    provider=llm_response.provider,
                    model=llm_response.model,
                    raw_response=llm_response.content,
                    parsed_response=payload.model_dump(mode="json"),
                    status="completed",
                    latency_ms=llm_response.latency_ms,
                    prompt_tokens=llm_response.prompt_tokens,
                    completion_tokens=llm_response.completion_tokens,
                    total_tokens=llm_response.total_tokens,
                )
            )
            self.agent_runs.update_status(agent_run, "completed", output_summary=payload.summary)
            version.summary = payload.summary[:2000]
            self.session.commit()
            return StudyPlanExplanationResponse(
                agent_run_id=agent_run.id,
                study_plan_id=plan.id,
                version_id=version.id,
                generated_at=agent_run.completed_at or datetime.now(timezone.utc),
                **payload.model_dump(),
            )
        except ValidationError as exc:
            self._record_failure(agent_run, llm_prompt, "LLM response did not match expected schema")
            raise LLMResponseValidationError("LLM response did not match expected schema") from exc
        except Exception as exc:
            self._record_failure(agent_run, llm_prompt, str(exc))
            raise

    def _record_failure(self, agent_run: AgentRun, llm_prompt: LLMPrompt, error_message: str) -> None:
        self.responses.attach_response(
            LLMResponse(
                agent_run_id=agent_run.id,
                llm_prompt_id=llm_prompt.id,
                provider="openai",
                model=settings.OPENAI_MODEL,
                status="failed",
                error_message=error_message,
            )
        )
        self.agent_runs.update_status(agent_run, "failed", error_message=error_message)
        self.session.commit()

    def _build_sanitized_context(self, user_id: UUID, plan_id: UUID, version_id: UUID) -> dict:
        plan = self.plans.get_by_id(plan_id)
        version = self.versions.get_by_id(version_id)
        if plan is None or version is None:
            raise PlanNotFoundError()
        goal = self.goals.get_by_id(plan.goal_id)
        sessions = self.sessions.list_by_version_id(version.id)
        tasks = self.tasks.list_by_session_ids([session.id for session in sessions])
        topics = [topic for topic in self.topics.list_by_goal_id(plan.goal_id) if topic.user_id == user_id]
        subjects = [subject for subject in self.subjects.list_by_goal_id(plan.goal_id) if subject.user_id == user_id]
        total_minutes = sum(session.planned_duration_minutes for session in sessions)
        dates = [session.session_date for session in sessions]
        upcoming_sample = sessions[:5]
        tasks_by_session = {session.id: [task for task in tasks if task.study_session_id == session.id][:3] for session in upcoming_sample}

        return {
            "goal_title": goal.title if goal else plan.title,
            "exam_date": goal.exam_date.isoformat() if goal else None,
            "subjects": [{"name": subject.name, "priority": subject.priority} for subject in subjects],
            "topics": [
                {
                    "name": topic.name,
                    "difficulty": topic.difficulty,
                    "priority": topic.priority,
                    "estimated_hours": str(topic.estimated_hours) if topic.estimated_hours is not None else None,
                }
                for topic in topics
            ],
            "session_count": len(sessions),
            "task_count": len(tasks),
            "date_range": {"start": min(dates).isoformat() if dates else None, "end": max(dates).isoformat() if dates else None},
            "total_planned_minutes": total_minutes,
            "planner_summary": version.summary,
            "upcoming_sessions_sample": [
                {
                    "date": session.session_date.isoformat(),
                    "start_time": session.start_time.isoformat() if session.start_time else None,
                    "duration_minutes": session.planned_duration_minutes,
                    "session_type": session.session_type,
                    "tasks": [
                        {"title": task.title, "task_type": task.task_type, "duration_minutes": task.planned_duration_minutes}
                        for task in tasks_by_session[session.id]
                    ],
                }
                for session in upcoming_sample
            ],
        }

