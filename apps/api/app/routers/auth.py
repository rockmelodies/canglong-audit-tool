from fastapi import APIRouter, Depends, HTTPException, status

from app.models.schemas import LoginRequest, LoginResponse, UserProfile
from app.services.auth_service import auth_service, get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    user = auth_service.authenticate(payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = auth_service.create_token(user)
    return LoginResponse(access_token=token, user=user)


@router.get("/me", response_model=UserProfile)
def me(current_user: UserProfile = Depends(get_current_user)) -> UserProfile:
    return current_user

