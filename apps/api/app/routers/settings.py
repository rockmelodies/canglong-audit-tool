from fastapi import APIRouter, Depends

from app.models.schemas import ModelConnection, ModelConnectionUpsert, ModelSettingsResponse, UserProfile
from app.services.auth_service import get_current_user
from app.services.model_settings import model_settings_store

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("/models", response_model=ModelSettingsResponse)
def get_model_settings(current_user: UserProfile = Depends(get_current_user)) -> ModelSettingsResponse:
    return model_settings_store.list_settings()


@router.post("/models", response_model=ModelConnection)
def create_model_settings(
    payload: ModelConnectionUpsert,
    current_user: UserProfile = Depends(get_current_user),
) -> ModelConnection:
    return model_settings_store.create_model(payload)


@router.put("/models/{model_id}", response_model=ModelConnection)
def update_model_settings(
    model_id: str,
    payload: ModelConnectionUpsert,
    current_user: UserProfile = Depends(get_current_user),
) -> ModelConnection:
    return model_settings_store.update_model(model_id, payload)


@router.post("/models/{model_id}/default", response_model=ModelConnection)
def set_default_model(model_id: str, current_user: UserProfile = Depends(get_current_user)) -> ModelConnection:
    return model_settings_store.set_default(model_id)
