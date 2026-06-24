from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security.auth_dependencies import get_current_user
from app.infrastructure.database.session import get_db
from app.modules.goals.schemas.requests import GoalCreateRequest, GoalUpdateRequest, SubjectCreateRequest, TopicCreateRequest
from app.modules.goals.schemas.responses import GoalResponse, SubjectResponse, TopicResponse
from app.modules.goals.services.goal_service import GoalService
from app.modules.users.infrastructure_models import User

router = APIRouter(tags=["goals"])


def success(message: str, data: object | None = None) -> dict:
    return {"success": True, "message": message, "data": data if data is not None else {}}


@router.post("/goals")
def create_goal(
    request: GoalCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    goal = GoalService(db).create_goal(current_user.id, request)
    data = GoalResponse.model_validate(goal)
    return success("Goal created successfully", data.model_dump(mode="json"))


@router.get("/goals")
def list_goals(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    goals = GoalService(db).list_goals(current_user.id)
    data = [GoalResponse.model_validate(goal).model_dump(mode="json") for goal in goals]
    return success("Goals fetched successfully", data)


@router.get("/goals/{goal_id}")
def get_goal(
    goal_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    goal = GoalService(db).get_goal(current_user.id, goal_id)
    data = GoalResponse.model_validate(goal)
    return success("Goal fetched successfully", data.model_dump(mode="json"))


@router.put("/goals/{goal_id}")
def update_goal(
    goal_id: UUID,
    request: GoalUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    goal = GoalService(db).update_goal(current_user.id, goal_id, request)
    data = GoalResponse.model_validate(goal)
    return success("Goal updated successfully", data.model_dump(mode="json"))


@router.delete("/goals/{goal_id}")
def archive_goal(
    goal_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    GoalService(db).archive_goal(current_user.id, goal_id)
    return success("Goal archived successfully")


@router.post("/goals/{goal_id}/subjects")
def create_subject(
    goal_id: UUID,
    request: SubjectCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    subject = GoalService(db).create_subject(current_user.id, goal_id, request)
    data = SubjectResponse.model_validate(subject)
    return success("Subject created successfully", data.model_dump(mode="json"))


@router.get("/goals/{goal_id}/subjects")
def list_subjects(
    goal_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    subjects = GoalService(db).list_subjects(current_user.id, goal_id)
    data = [SubjectResponse.model_validate(subject).model_dump(mode="json") for subject in subjects]
    return success("Subjects fetched successfully", data)


@router.post("/subjects/{subject_id}/topics")
def create_topic(
    subject_id: UUID,
    request: TopicCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    topic = GoalService(db).create_topic(current_user.id, subject_id, request)
    data = TopicResponse.model_validate(topic)
    return success("Topic created successfully", data.model_dump(mode="json"))


@router.get("/subjects/{subject_id}/topics")
def list_topics(
    subject_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    topics = GoalService(db).list_topics(current_user.id, subject_id)
    data = [TopicResponse.model_validate(topic).model_dump(mode="json") for topic in topics]
    return success("Topics fetched successfully", data)

