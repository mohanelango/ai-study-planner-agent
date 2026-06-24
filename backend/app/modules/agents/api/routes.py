from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security.auth_dependencies import get_current_user
from app.infrastructure.database.session import get_db
from app.modules.agents.services.study_plan_explanation_service import StudyPlanExplanationService
from app.modules.users.infrastructure_models import User

router = APIRouter(tags=["agents"])


def success(message: str, data: object | None = None) -> dict:
    return {"success": True, "message": message, "data": data if data is not None else {}}


@router.post("/plans/{plan_id}/explain")
def explain_study_plan(
    plan_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    version_id: UUID | None = Query(default=None),
) -> dict:
    data = StudyPlanExplanationService(db).explain(current_user.id, plan_id, version_id)
    return success("Study plan explanation generated successfully", data.model_dump(mode="json"))

