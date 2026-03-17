import type { DashboardData, LlmStackData, Mission } from '../types';

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:9000';

const dashboardFallback: DashboardData = {
  repository: 'monorepo://target/payment-gateway',
  codename: 'Canglong',
  confidence: '96.4%',
  focus: 'Deserialize boundary + auth bypass + dynamic trace replay',
  metrics: [
    { id: 'coverage', label: 'Semantic Coverage', value: '91%', delta: '+12%', tone: 'accent' },
    { id: 'findings', label: 'High-Signal Findings', value: '18', delta: '3 confirmed', tone: 'warning' },
    { id: 'breakpoints', label: 'Breakpoint Plans', value: '42', delta: '8 ready now', tone: 'accent' },
    { id: 'containers', label: 'Sandbox Profiles', value: '11', delta: '2 hot', tone: 'neutral' },
  ],
  flow: [
    { name: 'Ingress', count: '124', emphasis: 'taint roots' },
    { name: 'State Drift', count: '37', emphasis: 'auth drift' },
    { name: 'Danger Sink', count: '9', emphasis: 'RCE / SSRF' },
    { name: 'Verified', count: '3', emphasis: 'PoC chained' },
  ],
  capabilities: [
    {
      name: 'Human-Like Audit',
      summary: 'Semantic trace compression, evidence graph, and low-noise suspicion ranking.',
      depth: 'AST + CFG + call-chain scoring',
      status: 'Primary',
    },
    {
      name: 'Dynamic Breakpoint Orchestrator',
      summary: 'Turns suspicious paths into debuggable breakpoints and replay checkpoints.',
      depth: 'Runtime probe recipes',
      status: 'Armed',
    },
    {
      name: 'Decompiler Lane',
      summary: 'Reserved pipeline for APK/JAR/ELF/PE reverse engineering and symbol recovery.',
      depth: 'Multi-adapter queue',
      status: 'Queued',
    },
    {
      name: 'Docker Range Builder',
      summary: 'Builds isolated targets with fixture secrets, seed traffic, and exploit helpers.',
      depth: 'Compose template packs',
      status: 'Ready',
    },
  ],
  feed: [
    {
      time: '00:12',
      title: 'Unsafe deserialization branch surfaced',
      detail: 'Session cookie decoder reaches dynamic class loading without stable allowlist evidence.',
      tag: 'Critical path',
    },
    {
      time: '00:19',
      title: 'Breakpoint recipe generated',
      detail: 'Replay plan maps pre-auth request body to sink arguments in three frames.',
      tag: 'Dynamic',
    },
    {
      time: '00:27',
      title: 'Docker sandbox profile staged',
      detail: 'Redis + app + mock IdP stack emitted with deterministic seed data.',
      tag: 'Environment',
    },
  ],
  hotPaths: [
    {
      path: 'src/auth/SessionCodec.java',
      risk: 'Critical',
      evidence: 'Untrusted bytes touch object reconstruction after custom flag unwrap.',
    },
    {
      path: 'pkg/gateway/internal/router.go',
      risk: 'High',
      evidence: 'Privilege context reused across middleware short-circuit branch.',
    },
    {
      path: 'services/upload/handler.py',
      risk: 'Medium',
      evidence: 'Path normalization occurs after storage backend resolution.',
    },
  ],
};

const missionsFallback: Mission[] = [
  {
    id: 'm-001',
    name: 'Gateway Auth Drift',
    target: 'payment-gateway',
    mode: 'Semantic + Runtime',
    stage: 'Breakpoint ready',
    confidence: '93%',
    findings: 4,
    nextAction: 'Attach debugger to deserialization boundary',
  },
  {
    id: 'm-002',
    name: 'Supply Chain Sandbox',
    target: 'worker-image',
    mode: 'Docker deploy',
    stage: 'Profile staged',
    confidence: '88%',
    findings: 2,
    nextAction: 'Boot compose template and replay seed traffic',
  },
  {
    id: 'm-003',
    name: 'Decompiler Sweep',
    target: 'android-release.apk',
    mode: 'Reverse engineering',
    stage: 'Queued',
    confidence: '79%',
    findings: 0,
    nextAction: 'Recover symbols and API surfaces',
  },
];

const llmStackFallback: LlmStackData = {
  strategy:
    'Route each subtask to the model best suited for reasoning depth, context size, multimodal artifacts, tool use, deployment boundary, and cost.',
  providers: [
    {
      id: 'openai',
      name: 'OpenAI',
      category: 'Reasoning + tool use',
      fit: 'Exploit reasoning, agent orchestration, structured reports',
      strengths: ['Deep reasoning', 'Tool calling', 'Structured outputs'],
      deployment: 'API / Azure / gateway adapter',
    },
    {
      id: 'anthropic',
      name: 'Anthropic',
      category: 'Long-context review',
      fit: 'Large repo reading, contradiction analysis, review-heavy tasks',
      strengths: ['Long context', 'Careful review', 'Diff analysis'],
      deployment: 'API / enterprise proxy',
    },
    {
      id: 'gemini',
      name: 'Gemini',
      category: 'Multimodal analysis',
      fit: 'Decompiler artifacts, diagrams, binary screenshots, large summaries',
      strengths: ['Multimodal input', 'Wide context', 'Artifact understanding'],
      deployment: 'API / cloud workspace',
    },
    {
      id: 'qwen',
      name: 'Qwen',
      category: 'Open-weight agent lane',
      fit: 'Bilingual audit and private on-prem execution',
      strengths: ['Self-hosting', 'Code tasks', 'Chinese/English usage'],
      deployment: 'vLLM / SGLang / custom gateway',
    },
    {
      id: 'deepseek',
      name: 'DeepSeek',
      category: 'Cost-efficient reasoning',
      fit: 'Batch vulnerability sweeps and broad triage',
      strengths: ['Reasoning economy', 'Batch triage', 'Code comprehension'],
      deployment: 'API / compatible gateway',
    },
    {
      id: 'selfhosted',
      name: 'Self-hosted Mesh',
      category: 'Sensitive code isolation',
      fit: 'Air-gapped reviews and compliance-bound deployments',
      strengths: ['Private inference', 'Adapter control', 'Policy isolation'],
      deployment: 'Ollama / vLLM / internal serving',
    },
  ],
  blueprints: [
    {
      name: 'Exploit Chain Researcher',
      purpose: 'Expand one suspicious path into attack preconditions, pivots, and proof steps.',
      modelStrategy: 'Reasoning-first provider with low-cost sweep fallback.',
      outputs: ['Exploit hypotheses', 'Replay prompts', 'Proof checklist'],
      status: 'Primary',
    },
    {
      name: 'False-Positive Reducer',
      purpose: 'Cross-check framework guards, sanitizers, and deployment assumptions before severity promotion.',
      modelStrategy: 'Long-context reviewer paired with rule verification.',
      outputs: ['Contradiction log', 'Severity demotions', 'Evidence gaps'],
      status: 'Primary',
    },
    {
      name: 'Decompiler Recon Agent',
      purpose: 'Turn decompiled code and artifacts into an actionable attack-surface map.',
      modelStrategy: 'Multimodal-capable model with artifact adapters.',
      outputs: ['Recovered endpoints', 'Secret hints', 'Library notes'],
      status: 'Queued',
    },
    {
      name: 'Docker Range Planner',
      purpose: 'Convert exploit hypotheses into reproducible compose profiles and probes.',
      modelStrategy: 'Tool-using model with template registry access.',
      outputs: ['Compose plans', 'Fixture data', 'Probe recipes'],
      status: 'Ready',
    },
  ],
  runs: [
    {
      id: 'ar-001',
      agent: 'Exploit Chain Researcher',
      objective: 'Trace auth bypass into deserialization sink',
      provider: 'OpenAI',
      state: 'Running',
      result: 'Building exploit precondition matrix and replay prompts.',
    },
    {
      id: 'ar-002',
      agent: 'Framework Guard Auditor',
      objective: 'Check Spring and gateway guard rails for false-positive suppression',
      provider: 'Anthropic',
      state: 'Ready',
      result: 'Guard clauses normalized; 7 noisy paths demoted.',
    },
    {
      id: 'ar-003',
      agent: 'Binary Recon Agent',
      objective: 'Recover API surfaces from uploaded APK',
      provider: 'Gemini',
      state: 'Queued',
      result: 'Waiting for decompile lane and symbol index.',
    },
  ],
};

async function request<T>(path: string, fallback: T): Promise<T> {
  try {
    const response = await fetch(`${API_BASE}${path}`);
    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`);
    }
    return (await response.json()) as T;
  } catch {
    return fallback;
  }
}

export function fetchDashboard() {
  return request<DashboardData>('/api/dashboard', dashboardFallback);
}

export function fetchMissions() {
  return request<Mission[]>('/api/missions', missionsFallback);
}

export function fetchLlmStack() {
  return request<LlmStackData>('/api/llm/stack', llmStackFallback);
}
