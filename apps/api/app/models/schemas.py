from typing import Literal

from pydantic import BaseModel, Field


Tone = Literal["accent", "warning", "neutral"]
AuditStatus = Literal["queued", "running", "completed", "failed"]


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


class UserProfile(BaseModel):
    username: str
    displayName: str
    role: str


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile


class RepoConfig(BaseModel):
    id: str
    name: str
    provider: str
    url: str
    branch: str
    localPath: str
    status: str
    defaultBaseUrl: str | None = None
    lastSyncAt: str | None = None
    lastAuditAt: str | None = None
    summary: str


class RepoCreate(BaseModel):
    url: str
    branch: str = "main"
    name: str | None = None
    defaultBaseUrl: str | None = None


class RepoSyncResponse(BaseModel):
    repo: RepoConfig
    message: str


class AuditStage(BaseModel):
    name: str
    status: Literal["pending", "running", "completed", "failed"]
    detail: str


class EndpointRecord(BaseModel):
    method: str
    path: str
    framework: str
    handler: str
    file: str
    flow: list[str] = Field(default_factory=list)


class InterfaceTestPlan(BaseModel):
    method: str
    path: str
    objective: str
    payloadHint: str


class VulnerabilityFinding(BaseModel):
    id: str
    title: str
    category: str
    severity: Literal["critical", "high", "medium", "low"]
    file: str
    line: int
    summary: str
    evidence: str
    chain: list[str] = Field(default_factory=list)


class AuditJob(BaseModel):
    id: str
    repoId: str
    repoName: str
    status: AuditStatus
    progress: int
    currentStep: str
    findings: int
    endpoints: int
    createdAt: str
    updatedAt: str
    reportId: str | None = None
    stages: list[AuditStage] = Field(default_factory=list)
    error: str | None = None


class AuditJobCreate(BaseModel):
    repoId: str


class AuditSummary(BaseModel):
    filesScanned: int
    endpointsDiscovered: int
    businessFlowsMapped: int
    findingsTotal: int
    criticalFindings: int
    highFindings: int


class AuditReport(BaseModel):
    id: str
    jobId: str
    repoId: str
    repoName: str
    generatedAt: str
    summary: AuditSummary
    endpointMap: list[EndpointRecord]
    interfaceTests: list[InterfaceTestPlan]
    findings: list[VulnerabilityFinding]
    recommendations: list[str]
