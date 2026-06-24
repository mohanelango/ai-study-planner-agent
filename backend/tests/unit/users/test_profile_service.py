from datetime import time
import unittest

from app.core.exceptions.base import AppException
from app.modules.users.domain.rules import ensure_day_of_week, ensure_positive, ensure_time_window


class ProfileServiceUnitTestCase(unittest.TestCase):
    def test_profile_validation_rules(self) -> None:
        ensure_positive(30, "daily_goal_minutes")
        with self.assertRaises(AppException):
            ensure_positive(0, "daily_goal_minutes")

    def test_availability_validation_rules(self) -> None:
        ensure_day_of_week(0)
        ensure_day_of_week(6)
        ensure_time_window(time(9, 0), time(10, 0))
        with self.assertRaises(AppException):
            ensure_day_of_week(7)
        with self.assertRaises(AppException):
            ensure_time_window(time(10, 0), time(9, 0))


if __name__ == "__main__":
    unittest.main()

