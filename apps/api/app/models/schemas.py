from typing import Literal

from pydantic import BaseModel


Tone = Literal["accent", "warning", "neutral"]


class MetricCardItem(BaseModel):
    id: str
    label: str
    value: str
    delta: str
    tone: Tone


class FlowStage(BaseModel):
    name: str
    count: str
    emphasis: str


class CapabilityItem(BaseModel):
    name: str
    summary: str
    depth: str
    status: str


class FeedEvent(BaseModel):
    time: str
    title: str
    detail: str
    tag: str


class HotPath(BaseModel):
    path: str
    risk: str
    evidence: str


class ModelProvider(BaseModel):
    id: str
    name: str
    category: str
    fit: str
    strengths: list[str]
    deployment: str


class AgentBlueprint(BaseModel):
    name: str
    purpose: str
    modelStrategy: str
    outputs: list[str]
    status: str


class AgentRun(BaseModel):
    id: str
    agent: str
    objective: str
    provider: str
    state: str
    result: str


class LlmStackResponse(BaseModel):
    strategy: str
    providers: list[ModelProvider]
    blueprints: list[AgentBlueprint]
    runs: list[AgentRun]


class DashboardResponse(BaseModel):
    repository: str
    codename: str
    confidence: str
    focus: str
    metrics: list[MetricCardItem]
    flow: list[FlowStage]
    capabilities: list[CapabilityItem]
    feed: list[FeedEvent]
    hotPaths: list[HotPath]


class Mission(BaseModel):
    id: str
    name: str
    target: str
    mode: str
    stage: str
    confidence: str
    findings: int
    nextAction: str


class MissionCreate(BaseModel):
    name: str
    target: str
    mode: str


class ResearchAgentCreate(BaseModel):
    objective: str
    target: str
    preferredProvider: str | None = None
