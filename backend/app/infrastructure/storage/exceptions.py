from app.core.exceptions.base import AppException


class StorageConfigurationError(AppException):
    def __init__(self, message: str = "Storage is not configured") -> None:
        super().__init__(message=message, code="STORAGE_CONFIGURATION_ERROR", status_code=500)


class StorageUploadError(AppException):
    def __init__(self, message: str = "Failed to upload file") -> None:
        super().__init__(message=message, code="STORAGE_UPLOAD_ERROR", status_code=500)


class StorageDownloadError(AppException):
    def __init__(self, message: str = "Failed to download file") -> None:
        super().__init__(message=message, code="STORAGE_DOWNLOAD_ERROR", status_code=500)


class StorageDeleteError(AppException):
    def __init__(self, message: str = "Failed to delete file") -> None:
        super().__init__(message=message, code="STORAGE_DELETE_ERROR", status_code=500)

