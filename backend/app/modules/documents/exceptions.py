from app.core.exceptions.base import AppException


class DocumentNotFoundError(AppException):
    def __init__(self) -> None:
        super().__init__(message="Document not found", code="DOCUMENT_NOT_FOUND", status_code=404)


class InvalidDocumentUploadError(AppException):
    def __init__(self, message: str, code: str = "INVALID_DOCUMENT_UPLOAD") -> None:
        super().__init__(message=message, code=code, status_code=400)


class BackgroundJobNotFoundError(AppException):
    def __init__(self) -> None:
        super().__init__(message="Background job not found", code="BACKGROUND_JOB_NOT_FOUND", status_code=404)

