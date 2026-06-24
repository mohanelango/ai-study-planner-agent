from app.core.exceptions.base import AppException


class DocumentExtractionError(AppException):
    def __init__(self, message: str = "Could not extract text from document") -> None:
        super().__init__(message=message, code="DOCUMENT_EXTRACTION_ERROR", status_code=400)


class EmptyDocumentError(AppException):
    def __init__(self, message: str = "Document does not contain extractable text") -> None:
        super().__init__(message=message, code="EMPTY_DOCUMENT", status_code=400)


class UnsupportedDocumentError(AppException):
    def __init__(self, message: str = "Unsupported document type") -> None:
        super().__init__(message=message, code="UNSUPPORTED_DOCUMENT", status_code=400)

