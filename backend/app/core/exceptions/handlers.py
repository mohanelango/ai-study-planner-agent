from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions.base import AppException
from app.core.logging.logger import get_logger

logger = get_logger(__name__)


def _error_response(message: str, code: str, details: dict, status_code: int) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "message": message,
            "error": {
                "code": code,
                "details": details,
            },
        },
    )


async def app_exception_handler(_: Request, exc: AppException) -> JSONResponse:
    return _error_response(exc.message, exc.code, exc.details, exc.status_code)


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception for %s", request.url.path, exc_info=exc)
    return _error_response(
        message="Internal server error",
        code="INTERNAL_SERVER_ERROR",
        details={},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    return _error_response(
        message="Request validation failed",
        code="VALIDATION_ERROR",
        details={"errors": exc.errors()},
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
