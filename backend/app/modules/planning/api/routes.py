from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security.auth_dependencies import get_current_user
from app.infrastructure.database.session import get_db
from app.modules.planning.schemas.requests import GenerateStudyPlanRequest
from app.modules.planning.services.plan_version_service import PlanVersionService
from app.modules.planning.services.study_plan_service import StudyPlanService
from app.modules.users.infrastructure_models import User

router = APIRouter(tags=["planning"])


def success(message: str, data: object | None = None) -> dict:
    return {"success": True, "message": message, "data": data if data is not None else {}}


@router.post("/plans/generate")
def generate_study_plan(
    request: GenerateStudyPlanRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    data = StudyPlanService(db).generate_plan(current_user.id, request)
    return success("Study plan generated successfully", data.model_dump(mode="json"))


@router.get("/plans/{plan_id}")
def get_plan(
    plan_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    data = StudyPlanService(db).get_overview(current_user.id, plan_id)
    return success("Study plan fetched successfully", data.model_dump(mode="json"))


@router.get("/plans/{plan_id}/calendar")
def get_plan_calendar(
    plan_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    version_id: UUID | None = Query(default=None),
) -> dict:
    data = StudyPlanService(db).get_calendar(current_user.id, plan_id, start_date, end_date, version_id)
    return success("Study plan calendar fetched successfully", data.model_dump(mode="json"))


@router.get("/plans/{plan_id}/today")
def get_today_tasks(
    plan_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    data = StudyPlanService(db).get_today(current_user.id, plan_id)
    return success("Today's tasks fetched successfully", data.model_dump(mode="json"))


@router.get("/plans/{plan_id}/versions")
def list_versions(
    plan_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    data = [version.model_dump(mode="json") for version in PlanVersionService(db).list_versions(current_user.id, plan_id)]
    return success("Study plan versions fetched successfully", data)


@router.get("/plans/{plan_id}/versions/{version_id}")
def get_version(
    plan_id: UUID,
    version_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    data = PlanVersionService(db).get_version(current_user.id, plan_id, version_id)
    return success("Study plan version fetched successfully", data.model_dump(mode="json"))

