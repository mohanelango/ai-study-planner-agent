from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config.settings import settings
from app.core.exceptions.handlers import register_exception_handlers
from app.core.logging.logger import setup_logging
from app.modules.agents.api.routes import router as agents_router
from app.modules.documents.api.routes import router as documents_router
from app.modules.goals.api.routes import router as goals_router
from app.modules.health.api.routes import router as health_router
from app.modules.planning.api.routes import router as planning_router
from app.modules.users.api.routes import router as users_router


setup_logging()

app = FastAPI(title=settings.APP_NAME, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(health_router, prefix=settings.API_V1_PREFIX)
app.include_router(users_router, prefix=settings.API_V1_PREFIX)
app.include_router(goals_router, prefix=settings.API_V1_PREFIX)
app.include_router(planning_router, prefix=settings.API_V1_PREFIX)
app.include_router(agents_router, prefix=settings.API_V1_PREFIX)
app.include_router(documents_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def root() -> dict:
    return {
        "success": True,
        "message": "AI Study Planner Agent API",
        "data": {
            "app_name": settings.APP_NAME,
            "environment": settings.APP_ENV,
        },
    }
