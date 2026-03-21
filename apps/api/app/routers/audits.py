from fastapi import APIRouter, Depends, HTTPException, status

from app.models.schemas import AuditJob, AuditJobCreate, AuditReport, UserProfile
from app.services.audit_engine import audit_service
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/audits", tags=["audits"])


@router.get("", response_model=list[AuditJob])
def list_audits(current_user: UserProfile = Depends(get_current_user)) -> list[AuditJob]:
    return audit_service.list_jobs()


@router.post("", response_model=AuditJob)
def start_audit(
    payload: AuditJobCreate,
    lang: str = "en",
    current_user: UserProfile = Depends(get_current_user),
) -> AuditJob:
    return audit_service.start_job(payload.repoId, lang)


@router.get("/{job_id}", response_model=AuditJob)
def get_audit(job_id: str, current_user: UserProfile = Depends(get_current_user)) -> AuditJob:
    return audit_service.get_job(job_id)


@router.get("/{job_id}/report", response_model=AuditReport)
def get_audit_report(job_id: str, current_user: UserProfile = Depends(get_current_user)) -> AuditReport:
    job = audit_service.get_job(job_id)
    if not job.reportId:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Audit report is not ready yet.")
    return audit_service.get_report(job.reportId)
