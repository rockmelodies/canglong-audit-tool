from fastapi import APIRouter, Depends, Query, status

from app.models.schemas import AgentRun, LlmStackResponse, ResearchAgentCreate, UserProfile
from app.services.auth_service import get_current_user
from app.services.mock_data import agent_run_store, build_llm_stack, normalize_locale

router = APIRouter(prefix="/api/llm", tags=["llm"])


@router.get("/stack", response_model=LlmStackResponse)
def get_llm_stack(
    lang: str = Query(default="en"),
    current_user: UserProfile = Depends(get_current_user),
) -> LlmStackResponse:
    return build_llm_stack(lang)


@router.post("/research-agents", response_model=AgentRun, status_code=status.HTTP_201_CREATED)
def create_research_agent(
    payload: ResearchAgentCreate,
    lang: str = Query(default="en"),
    current_user: UserProfile = Depends(get_current_user),
) -> AgentRun:
    locale = normalize_locale(lang)
    provider = payload.preferredProvider or ("GPT-5.4" if locale == "zh-CN" else "GPT-5.4")
    run = AgentRun(
        id=agent_run_store.next_id(),
        agent="调研 Agent" if locale == "zh-CN" else "Research Agent",
        objective=f"{payload.objective} @ {payload.target}",
        provider=provider,
        state="排队中" if locale == "zh-CN" else "Queued",
        result="等待提示词包、MCP 上下文与工具链装配。" if locale == "zh-CN" else "Pending prompt-pack selection, MCP context packing, and toolchain plan.",
        stack="GPT-5.4 + Audit Prompt Pack + Repository MCP + Runtime Toolchain",
    )
    return agent_run_store.add_run(run)
