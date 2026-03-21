from __future__ import annotations

import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4

from fastapi import HTTPException, status

from app.models.schemas import RepoConfig


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[4] / "workspace" / "repos"


def slugify(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", value).strip("-").lower()


def infer_repo_name(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.rstrip("/")
    candidate = path.split("/")[-1] if path else "repository"
    if candidate.endswith(".git"):
        candidate = candidate[:-4]
    return candidate or "repository"


class RepoStore:
    def __init__(self) -> None:
        self._repos: list[RepoConfig] = []

    def list_repos(self) -> list[RepoConfig]:
        return self._repos

    def get_repo(self, repo_id: str) -> RepoConfig:
        for repo in self._repos:
            if repo.id == repo_id:
                return repo
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")

    def create_repo(
        self,
        source_type: str,
        url: str | None,
        branch: str,
        name: str | None,
        default_base_url: str | None,
        local_path: str | None,
    ) -> RepoConfig:
        if source_type == "local":
            if not local_path:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Local path is required")
            resolved_path = Path(local_path).expanduser().resolve()
            if not resolved_path.exists() or not resolved_path.is_dir():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Local path does not exist")
            repo_name = name or resolved_path.name
            repo_path = resolved_path
            provider = "local"
            repo_url = str(resolved_path)
            summary = "Local workspace registered and ready for static audit."
        else:
            if not url:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Repository URL is required")
            repo_name = name or infer_repo_name(url)
            repo_path = workspace_root() / slugify(repo_name)
            provider = "github" if "github.com" in url.lower() else "git"
            repo_url = url
            summary = "Repository registered and waiting for first sync."
        repo = RepoConfig(
            id=f"repo-{uuid4().hex[:8]}",
            name=repo_name,
            provider=provider,
            sourceType="local" if source_type == "local" else "git",
            url=repo_url,
            branch=branch,
            localPath=str(repo_path),
            status="idle",
            defaultBaseUrl=default_base_url,
            summary=summary,
        )
        self._repos.insert(0, repo)
        return repo

    def update_repo(self, updated_repo: RepoConfig) -> RepoConfig:
        for index, repo in enumerate(self._repos):
            if repo.id == updated_repo.id:
                self._repos[index] = updated_repo
                return updated_repo
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")


repo_store = RepoStore()


def sync_repo(repo: RepoConfig) -> tuple[RepoConfig, str]:
    if repo.sourceType == "local":
        local_path = Path(repo.localPath)
        if not local_path.exists() or not local_path.is_dir():
            repo.status = "sync_failed"
            repo.summary = "Local path is no longer available."
            repo_store.update_repo(repo)
            raise HTTPException(status_code=status.HTTP_410_GONE, detail=repo.summary)

        repo.status = "ready"
        repo.lastSyncAt = utc_now()
        repo.summary = f"Local workspace verified: {repo.localPath}"
        repo_store.update_repo(repo)
        return repo, repo.summary

    repo_path = Path(repo.localPath)
    repo_path.parent.mkdir(parents=True, exist_ok=True)

    if repo_path.exists() and (repo_path / ".git").exists():
        command = ["git", "-C", str(repo_path), "pull", "--ff-only", "origin", repo.branch]
        message_prefix = "Repository updated"
    else:
        if repo_path.exists() and not (repo_path / ".git").exists():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Path exists but is not a git repository: {repo_path}",
            )
        command = ["git", "clone", "--depth", "1", "--branch", repo.branch, repo.url, str(repo_path)]
        message_prefix = "Repository cloned"

    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        repo.status = "sync_failed"
        repo.summary = (result.stderr or result.stdout).strip() or "Git operation failed."
        repo_store.update_repo(repo)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=repo.summary)

    repo.status = "ready"
    repo.lastSyncAt = utc_now()
    repo.summary = f"{message_prefix} from {repo.url}"
    repo_store.update_repo(repo)
    return repo, (result.stdout or result.stderr).strip() or message_prefix
