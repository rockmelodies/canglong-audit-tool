from typing import Literal

from pydantic import BaseModel, Field


Tone = Literal["accent", "warning", "neutral"]
AuditStatus = Literal["queued", "running", "completed", "failed"]
ApplicabilityStatus = Literal["applicable", "blocked", "uncertain"]

# 审计类型定义 / Audit Type Definitions
AuditType = Literal["sast", "dast", "sca", "secret", "comprehensive"]

# 审计类型显示信息 / Audit Type Display Info
AUDIT_TYPE_INFO = {
    "sast": {
        "code": "sast",
        "name": "SAST",
        "fullName": "静态应用安全测试",
        "fullNameEn": "Static Application Security Testing",
        "description": "源代码静态分析，检测安全漏洞",
        "descriptionEn": "Static code analysis to detect security vulnerabilities",
        "icon": "🔍",
        "color": "#3B82F6",
        "bgColor": "#EFF6FF",
        "borderColor": "#BFDBFE"
    },
    "dast": {
        "code": "dast",
        "name": "DAST",
        "fullName": "动态应用安全测试",
        "fullNameEn": "Dynamic Application Security Testing",
        "description": "运行时安全测试，模拟攻击",
        "descriptionEn": "Runtime security testing, simulating attacks",
        "icon": "🎯",
        "color": "#F97316",
        "bgColor": "#FFF7ED",
        "borderColor": "#FED7AA"
    },
    "sca": {
        "code": "sca",
        "name": "SCA",
        "fullName": "软件成分分析",
        "fullNameEn": "Software Composition Analysis",
        "description": "依赖漏洞扫描，许可证合规",
        "descriptionEn": "Dependency vulnerability scanning, license compliance",
        "icon": "📦",
        "color": "#8B5CF6",
        "bgColor": "#F5F3FF",
        "borderColor": "#DDD6FE"
    },
    "secret": {
        "code": "secret",
        "name": "SECRET",
        "fullName": "敏感信息检测",
        "fullNameEn": "Secret Detection",
        "description": "检测代码中的密钥、凭证",
        "descriptionEn": "Detect keys and credentials in code",
        "icon": "🔑",
        "color": "#EF4444",
        "bgColor": "#FEF2F2",
        "borderColor": "#FECACA"
    },
    "comprehensive": {
        "code": "comprehensive",
        "name": "综合",
        "fullName": "综合审计",
        "fullNameEn": "Comprehensive Audit",
        "description": "全量安全审计，包含以上所有",
        "descriptionEn": "Full security audit including all above",
        "icon": "🛡️",
        "color": "#10B981",
        "bgColor": "#ECFDF5",
        "borderColor": "#A7F3D0"
    }
}


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
    priority: str | None = None
    augmentation: list[str] = Field(default_factory=list)


class EnablementLayer(BaseModel):
    id: str
    name: str
    kind: Literal["prompt-pack", "mcp", "toolchain", "skill-pack", "policy"]
    summary: str
    impact: str


class AgentBlueprint(BaseModel):
    name: str
    purpose: str
    modelStrategy: str
    outputs: list[str]
    status: str
    defaultModel: str | None = None
    enablement: list[str] = Field(default_factory=list)


class AgentRun(BaseModel):
    id: str
    agent: str
    objective: str
    provider: str
    state: str
    result: str
    stack: str | None = None


class LlmStackResponse(BaseModel):
    strategy: str
    providers: list[ModelProvider]
    enablement: list[EnablementLayer]
    blueprints: list[AgentBlueprint]
    runs: list[AgentRun]


class ModelConnection(BaseModel):
    id: str
    displayName: str
    provider: str
    modelSlug: str
    description: str
    baseUrl: str
    apiKeySet: bool = False
    apiKeyPreview: str | None = None
    enabled: bool = False
    isDefault: bool = False
    editable: bool = True
    status: Literal["configured", "incomplete"] = "incomplete"
    setupHint: str
    capabilityTags: list[str] = Field(default_factory=list)


class ModelConnectionUpsert(BaseModel):
    displayName: str
    provider: str
    modelSlug: str
    description: str
    baseUrl: str
    apiKey: str | None = None
    enabled: bool = False
    capabilityTags: list[str] = Field(default_factory=list)


class ModelSettingsResponse(BaseModel):
    recommendedModelId: str | None = None
    hasUsableModel: bool = False
    defaultModelLabel: str | None = None
    nextAction: str
    guidance: list[str] = Field(default_factory=list)
    models: list[ModelConnection] = Field(default_factory=list)


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
    sourceType: Literal["git", "local"]
    url: str
    branch: str
    localPath: str
    status: str
    defaultBaseUrl: str | None = None
    lastSyncAt: str | None = None
    lastAuditAt: str | None = None
    summary: str


class RepoCreate(BaseModel):
    sourceType: Literal["git", "local"] = "git"
    url: str | None = None
    branch: str = "main"
    name: str | None = None
    defaultBaseUrl: str | None = None
    localPath: str | None = None


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


class DependencyEvidence(BaseModel):
    ecosystem: str
    name: str
    version: str | None = None
    sourceFile: str
    scope: str | None = None


class EnvironmentFingerprint(BaseModel):
    languages: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)
    buildFiles: list[str] = Field(default_factory=list)
    javaVersionHint: str | None = None
    servletNamespace: str | None = None
    runtimeHints: list[str] = Field(default_factory=list)
    packaging: list[str] = Field(default_factory=list)


class ApplicabilityCheck(BaseModel):
    target: str
    status: ApplicabilityStatus
    reason: str


class ExploitChainCandidate(BaseModel):
    id: str
    name: str
    category: str
    confidence: str
    rationale: str
    prerequisites: list[str] = Field(default_factory=list)
    matchedDependencies: list[str] = Field(default_factory=list)
    sourceFindings: list[str] = Field(default_factory=list)
    checks: list[ApplicabilityCheck] = Field(default_factory=list)
    nextStep: str


class FalsePositiveControl(BaseModel):
    rule: str
    verdict: Literal["kept", "demoted", "blocked"]
    detail: str


class DockerVerification(BaseModel):
    status: Literal["skipped", "planned", "running", "completed", "failed"]
    strategy: str
    dockerfile: str | None = None
    composeFile: str | None = None
    imageTag: str | None = None
    containerName: str | None = None
    commands: list[str] = Field(default_factory=list)
    logs: list[str] = Field(default_factory=list)
    requiresLogin: bool = False
    loginHint: str | None = None


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
    verificationStatus: Literal["skipped", "planned", "running", "completed", "failed"] = "skipped"
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
    environment: EnvironmentFingerprint
    dependencies: list[DependencyEvidence]
    exploitChains: list[ExploitChainCandidate]
    falsePositiveControls: list[FalsePositiveControl]
    dockerVerification: DockerVerification
    endpointMap: list[EndpointRecord]
    interfaceTests: list[InterfaceTestPlan]
    findings: list[VulnerabilityFinding]
    recommendations: list[str]


# User Management Models
UserRole = Literal["administrator", "auditor", "viewer"]
ApiKeyStatus = Literal["active", "revoked", "expired"]
InviteStatus = Literal["pending", "accepted", "expired", "revoked"]


class UserCreate(BaseModel):
    username: str
    password: str
    displayName: str
    email: str | None = None
    role: UserRole = "viewer"


class UserUpdate(BaseModel):
    displayName: str | None = None
    email: str | None = None
    role: UserRole | None = None
    isActive: bool | None = None


class UserResponse(BaseModel):
    username: str
    displayName: str
    email: str | None
    role: UserRole
    isActive: bool
    createdAt: str
    lastLogin: str | None


class ApiKeyCreate(BaseModel):
    name: str
    permissions: list[str] = Field(default_factory=lambda: ["read"])
    expiresAt: str | None = None


class ApiKeyResponse(BaseModel):
    id: str
    name: str
    key: str | None = None  # Only returned on creation
    userId: str
    permissions: list[str]
    status: ApiKeyStatus
    createdAt: str
    expiresAt: str | None
    lastUsed: str | None


class UserInviteCreate(BaseModel):
    email: str
    role: UserRole = "viewer"


class UserInviteResponse(BaseModel):
    """用户邀请响应模型 / User invitation response model

    用于返回用户邀请的详细信息，包括邀请链接、状态等。
    Used to return detailed information about user invitations, including invite links and status.

    Attributes:
        id: 邀请ID / Invitation ID
        email: 被邀请用户邮箱 / Email of invited user
        role: 分配的角色 / Assigned role
        invitedBy: 邀请人用户名 / Username of inviter
        createdAt: 邀请创建时间 / Invitation creation time
        expiresAt: 邀请过期时间 / Invitation expiration time
        status: 邀请状态 / Invitation status
        inviteLink: 邀请链接（仅在创建时返回）/ Invite link (only returned on creation)
    """
    id: str
    email: str
    role: UserRole
    invitedBy: str
    createdAt: str
    expiresAt: str
    status: InviteStatus
    inviteLink: str | None = None  # Only returned on creation


class AcceptInviteRequest(BaseModel):
    """接受邀请请求模型 / Accept invitation request model

    用于用户接受邀请时提交的请求体，包含用户注册信息。
    Used for the request body when a user accepts an invitation, containing user registration information.

    Attributes:
        username: 用户名（3-32字符，字母开头，仅包含字母、数字和下划线）/ Username (3-32 chars, starts with letter, alphanumeric + underscore only)
        password: 密码（至少8位，必须包含大小写字母、数字和特殊字符）/ Password (min 8 chars, must contain uppercase, lowercase, digit, and special char)
        displayName: 显示名称 / Display name
    """
    username: str = Field(
        ...,
        min_length=3,
        max_length=32,
        pattern=r'^[a-zA-Z][a-zA-Z0-9_]*$',
        description="用户名，3-32字符，字母开头，仅包含字母、数字和下划线 / Username, 3-32 chars, starts with letter, alphanumeric + underscore only"
    )
    password: str = Field(
        ...,
        min_length=8,
        description="密码，至少8位，必须包含大小写字母、数字和特殊字符 / Password, min 8 chars, must contain uppercase, lowercase, digit, and special char"
    )
    displayName: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="显示名称 / Display name"
    )


class UserListResponse(BaseModel):
    users: list[UserResponse]
    total: int


class ApiKeyListResponse(BaseModel):
    keys: list[ApiKeyResponse]
    total: int


class PermissionCheck(BaseModel):
    resource: str
    action: str
    allowed: bool
    reason: str | None = None


# ==================== Project Management Models ====================
# 项目管理模型 / Project Management Models

class ProjectRepository(BaseModel):
    """项目仓库信息 / Project repository information
    
    Attributes:
        type: 仓库类型 (git/local) / Repository type (git/local)
        url: Git仓库URL / Git repository URL
        localPath: 本地路径 / Local path
        branch: 分支名称 / Branch name
        lastSyncAt: 最后同步时间 / Last sync time
        syncStatus: 同步状态 / Sync status
    """
    type: Literal["git", "local"]
    url: str | None = None
    localPath: str | None = None
    branch: str = "main"
    lastSyncAt: str | None = None
    syncStatus: Literal["idle", "syncing", "success", "failed"] = "idle"


class ProjectStatistics(BaseModel):
    """项目统计信息 / Project statistics
    
    Attributes:
        totalAudits: 总审计次数 / Total audit count
        lastAuditAt: 最后审计时间 / Last audit time
        totalFindings: 总发现数 / Total findings count
        criticalFindings: 严重漏洞数 / Critical findings count
        highFindings: 高危漏洞数 / High findings count
    """
    totalAudits: int = 0
    lastAuditAt: str | None = None
    totalFindings: int = 0
    criticalFindings: int = 0
    highFindings: int = 0


class ProjectSettings(BaseModel):
    """项目设置 / Project settings
    
    Attributes:
        defaultAuditType: 默认审计类型 / Default audit type
        autoSync: 自动同步 / Auto sync
        notifications: 通知开关 / Notifications enabled
    """
    defaultAuditType: AuditType = "comprehensive"
    autoSync: bool = False
    notifications: bool = True


class Project(BaseModel):
    """项目模型 / Project model
    
    Attributes:
        id: 项目ID / Project ID
        name: 项目名称 / Project name
        description: 项目描述 / Project description
        repository: 仓库信息 / Repository information
        statistics: 统计信息 / Statistics
        settings: 项目设置 / Project settings
        createdAt: 创建时间 / Creation time
        updatedAt: 更新时间 / Update time
    """
    id: str
    name: str
    description: str | None = None
    repository: ProjectRepository
    statistics: ProjectStatistics = Field(default_factory=ProjectStatistics)
    settings: ProjectSettings = Field(default_factory=ProjectSettings)
    createdAt: str
    updatedAt: str


class ProjectCreate(BaseModel):
    """创建项目请求 / Create project request
    
    Attributes:
        name: 项目名称 / Project name
        description: 项目描述 / Project description
        repository: 仓库信息 / Repository information
        settings: 项目设置 / Project settings
    """
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    repository: ProjectRepository
    settings: ProjectSettings = Field(default_factory=ProjectSettings)


class ProjectUpdate(BaseModel):
    """更新项目请求 / Update project request
    
    Attributes:
        name: 项目名称 / Project name
        description: 项目描述 / Project description
        settings: 项目设置 / Project settings
    """
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    settings: ProjectSettings | None = None


class ProjectListResponse(BaseModel):
    """项目列表响应 / Project list response
    
    Attributes:
        projects: 项目列表 / List of projects
        total: 总数 / Total count
    """
    projects: list[Project]
    total: int


# ==================== Enhanced Audit Task Models ====================
# 增强的审计任务模型 / Enhanced Audit Task Models

class AuditTaskConfig(BaseModel):
    """审计任务配置 / Audit task configuration
    
    Attributes:
        scope: 扫描范围 / Scan scope
        rules: 规则集 / Rule set
        excludePatterns: 排除模式 / Exclude patterns
        runtimeUrl: 运行时地址（用于DAST）/ Runtime URL (for DAST)
    """
    scope: list[str] = Field(default_factory=list)
    rules: list[str] = Field(default_factory=list)
    excludePatterns: list[str] = Field(default_factory=list)
    runtimeUrl: str | None = None


class AuditTaskResult(BaseModel):
    """审计任务结果 / Audit task result
    
    Attributes:
        filesScanned: 扫描文件数 / Files scanned
        findingsTotal: 总发现数 / Total findings
        findingsBySeverity: 按严重程度分类的发现数 / Findings by severity
        duration: 执行时长（秒）/ Duration in seconds
    """
    filesScanned: int = 0
    findingsTotal: int = 0
    findingsBySeverity: dict[str, int] = Field(default_factory=dict)
    duration: int = 0


class AuditTask(BaseModel):
    """审计任务模型 / Audit task model
    
    Attributes:
        id: 任务ID / Task ID
        projectId: 项目ID / Project ID
        projectName: 项目名称 / Project name
        type: 审计类型 / Audit type
        status: 任务状态 / Task status
        progress: 进度百分比 / Progress percentage
        currentStep: 当前步骤 / Current step
        config: 任务配置 / Task configuration
        result: 任务结果 / Task result
        error: 错误信息 / Error message
        createdAt: 创建时间 / Creation time
        startedAt: 开始时间 / Start time
        completedAt: 完成时间 / Completion time
    """
    id: str
    projectId: str
    projectName: str
    type: AuditType
    status: AuditStatus
    progress: int = 0
    currentStep: str | None = None
    config: AuditTaskConfig = Field(default_factory=AuditTaskConfig)
    result: AuditTaskResult | None = None
    error: str | None = None
    createdAt: str
    startedAt: str | None = None
    completedAt: str | None = None


class AuditTaskCreate(BaseModel):
    """创建审计任务请求 / Create audit task request
    
    Attributes:
        projectId: 项目ID / Project ID
        type: 审计类型 / Audit type
        config: 任务配置 / Task configuration
    """
    projectId: str
    type: AuditType = "comprehensive"
    config: AuditTaskConfig = Field(default_factory=AuditTaskConfig)


class AuditTaskListResponse(BaseModel):
    """审计任务列表响应 / Audit task list response
    
    Attributes:
        tasks: 任务列表 / List of tasks
        total: 总数 / Total count
    """
    tasks: list[AuditTask]
    total: int


class AuditTypeResponse(BaseModel):
    """审计类型响应 / Audit type response
    
    Attributes:
        code: 类型代码 / Type code
        name: 类型名称 / Type name
        fullName: 完整名称 / Full name
        fullNameEn: 英文完整名称 / Full name in English
        description: 描述 / Description
        descriptionEn: 英文描述 / Description in English
        icon: 图标 / Icon
        color: 颜色 / Color
        bgColor: 背景色 / Background color
        borderColor: 边框色 / Border color
    """
    code: str
    name: str
    fullName: str
    fullNameEn: str
    description: str
    descriptionEn: str
    icon: str
    color: str
    bgColor: str
    borderColor: str
