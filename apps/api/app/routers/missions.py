from fastapi import APIRouter, Depends, Query, status

from app.models.schemas import Mission, MissionCreate, UserProfile
from app.services.auth_service import get_current_user
from app.services.mock_data import mission_store, normalize_locale

router = APIRouter(prefix="/api", tags=["missions"])


@router.get("/missions", response_model=list[Mission])
def list_missions(
    lang: str = Query(default="en"),
    current_user: UserProfile = Depends(get_current_user),
) -> list[Mission]:
    return mission_store.list_missions(lang)


@router.post("/missions", response_model=Mission, status_code=status.HTTP_201_CREATED)
def create_mission(
    payload: MissionCreate,
    lang: str = Query(default="en"),
    current_user: UserProfile = Depends(get_current_user),
) -> Mission:
    locale = normalize_locale(lang)
    mission = Mission(
        id=mission_store.next_id(),
        name=payload.name,
        target=payload.target,
        mode=payload.mode,
        stage="排队中" if locale == "zh-CN" else "Queued",
        confidence="70%",
        findings=0,
        nextAction="等待证据图谱构建" if locale == "zh-CN" else "Awaiting evidence graph construction",
    )
    return mission_store.add_mission(mission)
