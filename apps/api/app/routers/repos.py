from fastapi import APIRouter, Depends

from app.models.schemas import RepoConfig, RepoCreate, RepoSyncResponse, UserProfile
from app.services.auth_service import get_current_user
from app.services.repo_manager import repo_store, sync_repo

router = APIRouter(prefix="/api/repos", tags=["repos"])


@router.get("", response_model=list[RepoConfig])
def list_repositories(current_user: UserProfile = Depends(get_current_user)) -> list[RepoConfig]:
    return repo_store.list_repos()


@router.post("", response_model=RepoConfig)
def create_repository(payload: RepoCreate, current_user: UserProfile = Depends(get_current_user)) -> RepoConfig:
    return repo_store.create_repo(
        payload.sourceType,
        payload.url,
        payload.branch,
        payload.name,
        payload.defaultBaseUrl,
        payload.localPath,
    )


@router.post("/{repo_id}/sync", response_model=RepoSyncResponse)
def sync_repository(repo_id: str, current_user: UserProfile = Depends(get_current_user)) -> RepoSyncResponse:
    repo = repo_store.get_repo(repo_id)
    updated_repo, message = sync_repo(repo)
    return RepoSyncResponse(repo=updated_repo, message=message)
