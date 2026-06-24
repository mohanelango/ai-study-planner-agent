from app.core.exceptions.base import AppException


class PlanNotFoundError(AppException):
    def __init__(self) -> None:
        super().__init__("Study plan not found", code="PLAN_NOT_FOUND", status_code=404)


class PlanVersionNotFoundError(AppException):
    def __init__(self) -> None:
        super().__init__("Study plan version not found", code="PLAN_VERSION_NOT_FOUND", status_code=404)


class DuplicateActivePlanError(AppException):
    def __init__(self) -> None:
        super().__init__("An active study plan already exists for this goal", code="DUPLICATE_ACTIVE_PLAN", status_code=409)


class PlanningValidationError(AppException):
    def __init__(self, message: str) -> None:
        super().__init__(message, code="PLANNING_VALIDATION_ERROR", status_code=422)

