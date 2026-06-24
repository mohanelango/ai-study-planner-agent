from datetime import date, datetime, time
from decimal import Decimal


class PlanningDomainError(ValueError):
    pass


def minutes_between(start_time: time, end_time: time) -> int:
    start = datetime.combine(date.today(), start_time)
    end = datetime.combine(date.today(), end_time)
    return max(0, int((end - start).total_seconds() // 60))


def default_hours_for_difficulty(difficulty: int) -> Decimal:
    mapping = {
        1: Decimal("1.0"),
        2: Decimal("1.5"),
        3: Decimal("2.0"),
        4: Decimal("3.0"),
        5: Decimal("4.0"),
    }
    return mapping.get(difficulty, Decimal("2.0"))


def topic_workload_minutes(estimated_hours: Decimal | None, difficulty: int) -> int:
    hours = estimated_hours if estimated_hours is not None else default_hours_for_difficulty(difficulty)
    difficulty_multiplier = Decimal("1.0") + (Decimal(max(difficulty, 1) - 1) * Decimal("0.10"))
    return int((hours * difficulty_multiplier * Decimal("60")).to_integral_value())

