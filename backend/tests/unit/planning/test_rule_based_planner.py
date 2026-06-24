from datetime import date, time, timedelta
from decimal import Decimal
import unittest
from uuid import uuid4

from app.modules.planning.domain.planner import RuleBasedPlanner
from app.modules.planning.domain.rules import PlanningDomainError
from app.modules.planning.domain.value_objects import PlannerAvailabilityWindow, PlannerGoal, PlannerTopic


class RuleBasedPlannerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.planner = RuleBasedPlanner()
        self.goal = PlannerGoal(id=uuid4(), title="Exam", exam_date=date.today() + timedelta(days=14))
        self.subject_id = uuid4()
        self.topic_easy = PlannerTopic(id=uuid4(), subject_id=self.subject_id, name="Easy", difficulty=1, priority=1, estimated_hours=Decimal("1"))
        self.topic_hard = PlannerTopic(id=uuid4(), subject_id=self.subject_id, name="Hard", difficulty=5, priority=5, estimated_hours=Decimal("1"))
        self.availability = [PlannerAvailabilityWindow(day_of_week=date.today().weekday(), start_time=time(9, 0), end_time=time(10, 0))]

    def test_rejects_no_topics(self) -> None:
        with self.assertRaises(PlanningDomainError):
            self.planner.generate(self.goal, [], self.availability, 60)

    def test_rejects_no_availability(self) -> None:
        with self.assertRaises(PlanningDomainError):
            self.planner.generate(self.goal, [self.topic_easy], [], 60)

    def test_generates_sessions_only_on_available_days_and_respects_duration(self) -> None:
        result = self.planner.generate(self.goal, [self.topic_easy], self.availability, 45, include_revision_sessions=False)
        self.assertGreater(len(result.sessions), 0)
        for session in result.sessions:
            self.assertEqual(session.session_date.weekday(), date.today().weekday())
            self.assertLessEqual(session.planned_duration_minutes, 45)
            self.assertLessEqual(sum(task.planned_duration_minutes for task in session.tasks), 45)

    def test_higher_priority_and_harder_topics_appear_earlier(self) -> None:
        result = self.planner.generate(self.goal, [self.topic_easy, self.topic_hard], self.availability, 60, include_revision_sessions=False)
        first_task = result.sessions[0].tasks[0]
        self.assertEqual(first_task.topic_id, self.topic_hard.id)


if __name__ == "__main__":
    unittest.main()

