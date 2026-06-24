from app.core.config.settings import settings
from app.infrastructure.database.session import check_database_connection


def get_dependency_statuses() -> dict[str, str]:
    return {
        "postgresql": "healthy" if check_database_connection() else "unhealthy",
        "redis": "not_checked",
        "qdrant": "not_checked",
        "minio": "not_checked",
        "openai": "configured" if settings.OPENAI_API_KEY else "not_configured",
    }
