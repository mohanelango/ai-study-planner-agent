from dataclasses import dataclass
from datetime import date, timedelta

from app.modules.planning.domain.rules import PlanningDomainError, minutes_between, topic_workload_minutes
from app.modules.planning.domain.value_objects import (
    GeneratedSession,
    GeneratedTask,
    PlannerAvailabilityWindow,
    PlannerGoal,
    PlannerResult,
    PlannerTopic,
)


@dataclass
class TopicWorkItem:
    topic: PlannerTopic
    remaining_minutes: int
    task_type: str = "learn"


class RuleBasedPlanner:
    def generate(
        self,
        goal: PlannerGoal,
        topics: list[PlannerTopic],
        availability_windows: list[PlannerAvailabilityWindow],
        preferred_session_minutes: int,
        include_revision_sessions: bool = True,
    ) -> PlannerResult:
        today = date.today()
        if goal.exam_date <= today:
            raise PlanningDomainError("Exam date must be in the future")
        if not topics:
            raise PlanningDomainError("At least one topic is required to generate a study plan")

        active_windows = [window for window in availability_windows if window.is_active and minutes_between(window.start_time, window.end_time) > 0]
        if not active_windows:
            raise PlanningDomainError("At least one active availability window is required")

        work_items = self._build_work_items(topics)
        total_required_minutes = sum(item.remaining_minutes for item in work_items)
        total_available_minutes = self._available_minutes_until_exam(today, goal.exam_date, active_windows)
        warnings: list[str] = []
        if total_available_minutes < total_required_minutes:
            warnings.append("Available study time is less than the estimated topic workload. The generated plan covers as much as possible before the exam.")

        sessions = self._fill_sessions(today, goal.exam_date, active_windows, work_items, preferred_session_minutes)
        if include_revision_sessions:
            sessions.extend(self._build_revision_sessions(goal.exam_date, active_windows, topics, preferred_session_minutes))
            sessions.sort(key=lambda session: (session.session_date, session.start_time is None, session.start_time))

        scheduled_minutes = sum(session.planned_duration_minutes for session in sessions)
        unscheduled_minutes = sum(item.remaining_minutes for item in work_items)
        if unscheduled_minutes > 0:
            warnings.append(f"{unscheduled_minutes} estimated minutes could not be scheduled before the exam.")

        summary = (
            f"Generated {len(sessions)} sessions and {sum(len(session.tasks) for session in sessions)} tasks "
            f"for {goal.title}. Scheduled {scheduled_minutes} minutes before {goal.exam_date.isoformat()}."
        )
        return PlannerResult(summary=summary, warnings=warnings, sessions=sessions)

    def _build_work_items(self, topics: list[PlannerTopic]) -> list[TopicWorkItem]:
        sorted_topics = sorted(topics, key=lambda topic: (-topic.priority, -topic.difficulty, topic.name.lower()))
        return [TopicWorkItem(topic=topic, remaining_minutes=topic_workload_minutes(topic.estimated_hours, topic.difficulty)) for topic in sorted_topics]

    def _available_minutes_until_exam(self, today: date, exam_date: date, windows: list[PlannerAvailabilityWindow]) -> int:
        total = 0
        current = today
        while current < exam_date:
            for window in windows:
                if current.weekday() == window.day_of_week:
                    total += minutes_between(window.start_time, window.end_time)
            current += timedelta(days=1)
        return total

    def _fill_sessions(
        self,
        today: date,
        exam_date: date,
        windows: list[PlannerAvailabilityWindow],
        work_items: list[TopicWorkItem],
        preferred_session_minutes: int,
    ) -> list[GeneratedSession]:
        sessions: list[GeneratedSession] = []
        current_day = today
        while current_day < exam_date and any(item.remaining_minutes > 0 for item in work_items):
            day_windows = sorted([window for window in windows if window.day_of_week == current_day.weekday()], key=lambda window: window.start_time)
            for window in day_windows:
                available_minutes = minutes_between(window.start_time, window.end_time)
                session_capacity = min(available_minutes, preferred_session_minutes)
                if session_capacity <= 0:
                    continue
                session = GeneratedSession(
                    session_date=current_day,
                    start_time=window.start_time,
                    end_time=window.end_time,
                    planned_duration_minutes=0,
                    session_type="study",
                    tasks=[],
                )
                remaining_capacity = session_capacity
                sort_order = 0
                while remaining_capacity > 0:
                    item = next((candidate for candidate in work_items if candidate.remaining_minutes > 0), None)
                    if item is None:
                        break
                    duration = min(item.remaining_minutes, remaining_capacity)
                    session.tasks.append(
                        self._task_from_topic(item.topic, duration, item.task_type, sort_order)
                    )
                    item.remaining_minutes -= duration
                    remaining_capacity -= duration
                    session.planned_duration_minutes += duration
                    sort_order += 1
                if session.tasks:
                    sessions.append(session)
            current_day += timedelta(days=1)
        return sessions

    def _build_revision_sessions(
        self,
        exam_date: date,
        windows: list[PlannerAvailabilityWindow],
        topics: list[PlannerTopic],
        preferred_session_minutes: int,
    ) -> list[GeneratedSession]:
        revision_topics = sorted(topics, key=lambda topic: (-topic.priority, -topic.difficulty, topic.name.lower()))[:3]
        if not revision_topics:
            return []

        sessions: list[GeneratedSession] = []
        current_day = max(date.today(), exam_date - timedelta(days=3))
        while current_day < exam_date and len(sessions) < len(revision_topics):
            day_windows = sorted([window for window in windows if window.day_of_week == current_day.weekday()], key=lambda window: window.start_time)
            for window in day_windows:
                if len(sessions) >= len(revision_topics):
                    break
                topic = revision_topics[len(sessions)]
                duration = min(30, preferred_session_minutes, minutes_between(window.start_time, window.end_time))
                if duration <= 0:
                    continue
                sessions.append(
                    GeneratedSession(
                        session_date=current_day,
                        start_time=window.start_time,
                        end_time=window.end_time,
                        planned_duration_minutes=duration,
                        session_type="revision",
                        tasks=[self._task_from_topic(topic, duration, "revise", 0)],
                    )
                )
            current_day += timedelta(days=1)
        return sessions

    @staticmethod
    def _task_from_topic(topic: PlannerTopic, duration: int, task_type: str, sort_order: int) -> GeneratedTask:
        action = "Revise" if task_type == "revise" else "Study"
        return GeneratedTask(
            topic_id=topic.id,
            subject_id=topic.subject_id,
            title=f"{action}: {topic.name}",
            description=f"{action.lower()} topic with priority {topic.priority} and difficulty {topic.difficulty}.",
            task_type=task_type,
            planned_duration_minutes=duration,
            sort_order=sort_order,
        )

