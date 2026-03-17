from fastapi import APIRouter, status

from app.models.schemas import AgentRun, LlmStackResponse, ResearchAgentCreate
from app.services.mock_data import agent_run_store, build_llm_stack

router = APIRouter(prefix="/api/llm", tags=["llm"])


@router.get("/stack", response_model=LlmStackResponse)
def get_llm_stack() -> LlmStackResponse:
    return build_llm_stack()


@router.post("/research-agents", response_model=AgentRun, status_code=status.HTTP_201_CREATED)
def create_research_agent(payload: ResearchAgentCreate) -> AgentRun:
    provider = payload.preferredProvider or "Router"
    run = AgentRun(
        id=agent_run_store.next_id(),
        agent="Research Agent",
        objective=f"{payload.objective} @ {payload.target}",
        provider=provider,
        state="Queued",
        result="Pending model selection, context packing, and tool plan.",
    )
    return agent_run_store.add_run(run)
