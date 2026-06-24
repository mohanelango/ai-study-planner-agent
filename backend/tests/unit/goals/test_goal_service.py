from datetime import date, timedelta
from decimal import Decimal
import unittest

from app.core.exceptions.base import AppException
from app.modules.goals.domain.rules import ensure_exam_date_not_past, ensure_non_empty, ensure_positive_decimal, ensure_rating


class GoalServiceUnitTestCase(unittest.TestCase):
    def test_goal_validation_rules(self) -> None:
        ensure_non_empty("Exam", "Goal title")
        ensure_exam_date_not_past(date.today() + timedelta(days=1))
        with self.assertRaises(AppException):
            ensure_non_empty(" ", "Goal title")
        with self.assertRaises(AppException):
            ensure_exam_date_not_past(date.today() - timedelta(days=1))

    def test_subject_topic_validation_rules(self) -> None:
        ensure_rating(1, "priority")
        ensure_rating(5, "difficulty")
        ensure_positive_decimal(Decimal("1.25"), "estimated_hours")
        with self.assertRaises(AppException):
            ensure_rating(0, "priority")
        with self.assertRaises(AppException):
            ensure_positive_decimal(Decimal("0"), "estimated_hours")


if __name__ == "__main__":
    unittest.main()

