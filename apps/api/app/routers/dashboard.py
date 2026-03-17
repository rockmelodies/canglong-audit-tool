from fastapi import APIRouter

from app.models.schemas import DashboardResponse
from app.services.mock_data import build_dashboard

router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard() -> DashboardResponse:
    return build_dashboard()

