import unittest

from app.modules.planning.services.schedule_generation_service import ScheduleGenerationService


class ScheduleGenerationServiceTestCase(unittest.TestCase):
    def test_service_class_exists(self) -> None:
        self.assertTrue(hasattr(ScheduleGenerationService, "generate"))


if __name__ == "__main__":
    unittest.main()

