export interface MetricCardItem {
  id: string;
  label: string;
  value: string;
  delta: string;
  tone: 'accent' | 'warning' | 'neutral';
}

export interface FlowStage {
  name: string;
  count: string;
  emphasis: string;
}

export interface CapabilityItem {
  name: string;
  summary: string;
  depth: string;
  status: string;
}

export interface FeedEvent {
  time: string;
  title: string;
  detail: string;
  tag: string;
}

export interface HotPath {
  path: string;
  risk: string;
  evidence: string;
}

export interface ModelProvider {
  id: string;
  name: string;
  category: string;
  fit: string;
  strengths: string[];
  deployment: string;
}

export interface AgentBlueprint {
  name: string;
  purpose: string;
  modelStrategy: string;
  outputs: string[];
  status: string;
}

export interface AgentRun {
  id: string;
  agent: string;
  objective: string;
  provider: string;
  state: string;
  result: string;
}

export interface DashboardData {
  repository: string;
  codename: string;
  confidence: string;
  focus: string;
  metrics: MetricCardItem[];
  flow: FlowStage[];
  capabilities: CapabilityItem[];
  feed: FeedEvent[];
  hotPaths: HotPath[];
}

export interface LlmStackData {
  strategy: string;
  providers: ModelProvider[];
  blueprints: AgentBlueprint[];
  runs: AgentRun[];
}

export interface Mission {
  id: string;
  name: string;
  target: string;
  mode: string;
  stage: string;
  confidence: string;
  findings: number;
  nextAction: string;
}

export interface UserProfile {
  username: string;
  displayName: string;
  role: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: UserProfile;
}

export interface RepoConfig {
  id: string;
  name: string;
  provider: string;
  sourceType: 'git' | 'local';
  url: string;
  branch: string;
  localPath: string;
  status: string;
  defaultBaseUrl: string | null;
  lastSyncAt: string | null;
  lastAuditAt: string | null;
  summary: string;
}

export interface RepoSyncResponse {
  repo: RepoConfig;
  message: string;
}

export interface AuditStage {
  name: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  detail: string;
}

export interface DependencyEvidence {
  ecosystem: string;
  name: string;
  version: string | null;
  sourceFile: string;
  scope: string | null;
}

export interface EnvironmentFingerprint {
  languages: string[];
  frameworks: string[];
  buildFiles: string[];
  javaVersionHint: string | null;
  servletNamespace: string | null;
  runtimeHints: string[];
  packaging: string[];
}

export interface ApplicabilityCheck {
  target: string;
  status: 'applicable' | 'blocked' | 'uncertain';
  reason: string;
}

export interface ExploitChainCandidate {
  id: string;
  name: string;
  category: string;
  confidence: string;
  rationale: string;
  prerequisites: string[];
  matchedDependencies: string[];
  sourceFindings: string[];
  checks: ApplicabilityCheck[];
  nextStep: string;
}

export interface FalsePositiveControl {
  rule: string;
  verdict: 'kept' | 'demoted' | 'blocked';
  detail: string;
}

export interface DockerVerification {
  status: 'skipped' | 'planned' | 'running' | 'completed' | 'failed';
  strategy: string;
  dockerfile: string | null;
  composeFile: string | null;
  imageTag: string | null;
  containerName: string | null;
  commands: string[];
  logs: string[];
  requiresLogin: boolean;
  loginHint: string | null;
}

export interface EndpointRecord {
  method: string;
  path: string;
  framework: string;
  handler: string;
  file: string;
  flow: string[];
}

export interface InterfaceTestPlan {
  method: string;
  path: string;
  objective: string;
  payloadHint: string;
}

export interface VulnerabilityFinding {
  id: string;
  title: string;
  category: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  file: string;
  line: number;
  summary: string;
  evidence: string;
  chain: string[];
}

export interface AuditJob {
  id: string;
  repoId: string;
  repoName: string;
  status: 'queued' | 'running' | 'completed' | 'failed';
  progress: number;
  currentStep: string;
  findings: number;
  endpoints: number;
  createdAt: string;
  updatedAt: string;
  reportId: string | null;
  verificationStatus: 'skipped' | 'planned' | 'running' | 'completed' | 'failed';
  stages: AuditStage[];
  error: string | null;
}

export interface AuditSummary {
  filesScanned: number;
  endpointsDiscovered: number;
  businessFlowsMapped: number;
  findingsTotal: number;
  criticalFindings: number;
  highFindings: number;
}

export interface AuditReport {
  id: string;
  jobId: string;
  repoId: string;
  repoName: string;
  generatedAt: string;
  summary: AuditSummary;
  environment: EnvironmentFingerprint;
  dependencies: DependencyEvidence[];
  exploitChains: ExploitChainCandidate[];
  falsePositiveControls: FalsePositiveControl[];
  dockerVerification: DockerVerification;
  endpointMap: EndpointRecord[];
  interfaceTests: InterfaceTestPlan[];
  findings: VulnerabilityFinding[];
  recommendations: string[];
}
