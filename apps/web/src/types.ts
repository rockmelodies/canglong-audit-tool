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
