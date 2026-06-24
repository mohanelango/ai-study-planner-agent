from fastapi import APIRouter

from app.core.config.settings import settings
from app.core.dependencies.health import get_dependency_statuses

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict:
    return {
        "success": True,
        "message": "Service is healthy",
        "data": {
            "service": settings.APP_NAME,
            "status": "healthy",
        },
    }


@router.get("/health/dependencies")
def dependency_health_check() -> dict:
    return {
        "success": True,
        "message": "Dependency status fetched successfully",
        "data": get_dependency_statuses(),
    }
