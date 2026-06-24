from app.core.exceptions.base import AppException


class DuplicateEmailError(AppException):
    def __init__(self) -> None:
        super().__init__("Email is already registered", code="DUPLICATE_EMAIL", status_code=409)


class InvalidCredentialsError(AppException):
    def __init__(self) -> None:
        super().__init__("Invalid email or password", code="INVALID_CREDENTIALS", status_code=401)


class ProfileAlreadyExistsError(AppException):
    def __init__(self) -> None:
        super().__init__("Profile already exists", code="PROFILE_ALREADY_EXISTS", status_code=409)


class ProfileNotFoundError(AppException):
    def __init__(self) -> None:
        super().__init__("Profile not found", code="PROFILE_NOT_FOUND", status_code=404)


class AvailabilityNotFoundError(AppException):
    def __init__(self) -> None:
        super().__init__("Availability window not found", code="AVAILABILITY_NOT_FOUND", status_code=404)

