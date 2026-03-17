from fastapi import APIRouter, status

from app.models.schemas import Mission, MissionCreate
from app.services.mock_data import mission_store

router = APIRouter(prefix="/api", tags=["missions"])


@router.get("/missions", response_model=list[Mission])
def list_missions() -> list[Mission]:
    return mission_store.list_missions()


@router.post("/missions", response_model=Mission, status_code=status.HTTP_201_CREATED)
def create_mission(payload: MissionCreate) -> Mission:
    mission = Mission(
        id=mission_store.next_id(),
        name=payload.name,
        target=payload.target,
        mode=payload.mode,
        stage="Queued",
        confidence="70%",
        findings=0,
        nextAction="Awaiting evidence graph construction",
    )
    return mission_store.add_mission(mission)

