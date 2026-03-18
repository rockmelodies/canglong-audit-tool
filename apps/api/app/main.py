from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.audits import router as audits_router
from app.routers.auth import router as auth_router
from app.routers.dashboard import router as dashboard_router
from app.routers.llm import router as llm_router
from app.routers.missions import router as missions_router
from app.routers.repos import router as repos_router

app = FastAPI(
    title="Canglong API",
    description="Orchestration API for code audit, vulnerability research, and sandbox execution.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard_router)
app.include_router(llm_router)
app.include_router(missions_router)
app.include_router(auth_router)
app.include_router(repos_router)
app.include_router(audits_router)


@app.get("/healthz", tags=["system"])
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
