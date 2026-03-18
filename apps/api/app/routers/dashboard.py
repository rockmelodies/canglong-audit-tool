from fastapi import APIRouter, Depends, Query

from app.models.schemas import DashboardResponse, UserProfile
from app.services.auth_service import get_current_user
from app.services.mock_data import build_dashboard

router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(
    lang: str = Query(default="en"),
    current_user: UserProfile = Depends(get_current_user),
) -> DashboardResponse:
    return build_dashboard(lang)
