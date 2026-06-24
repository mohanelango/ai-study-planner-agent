from app.core.exceptions.base import AppException


class GoalNotFoundError(AppException):
    def __init__(self) -> None:
        super().__init__("Goal not found", code="GOAL_NOT_FOUND", status_code=404)


class SubjectNotFoundError(AppException):
    def __init__(self) -> None:
        super().__init__("Subject not found", code="SUBJECT_NOT_FOUND", status_code=404)


class TopicNotFoundError(AppException):
    def __init__(self) -> None:
        super().__init__("Topic not found", code="TOPIC_NOT_FOUND", status_code=404)

