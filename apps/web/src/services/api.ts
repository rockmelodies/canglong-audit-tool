import { clearSession, getAccessToken } from '../auth/session';
import type { Locale } from '../i18n/messages';
import type {
  AuditJob,
  AuditReport,
  DashboardData,
  LlmStackData,
  Mission,
  RepoConfig,
  RepoSyncResponse,
} from '../types';

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:9000';

class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

function isChinese(locale: Locale) {
  return locale === 'zh-CN';
}

async function request<T>(
  path: string,
  locale: Locale,
  options?: RequestInit,
  fallback?: T,
): Promise<T> {
  const headers = new Headers(options?.headers ?? {});
  const token = getAccessToken();

  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  if (!headers.has('Content-Type') && options?.body) {
    headers.set('Content-Type', 'application/json');
  }

  const separator = path.includes('?') ? '&' : '?';
  try {
    const response = await fetch(`${API_BASE}${path}${separator}lang=${encodeURIComponent(locale)}`, {
      ...options,
      headers,
    });

    if (response.status === 401) {
      clearSession();
      throw new ApiError(401, 'Unauthorized');
    }

    if (!response.ok) {
      const detail = await response.text();
      throw new ApiError(response.status, detail || `Request failed: ${response.status}`);
    }

    return (await response.json()) as T;
  } catch (error) {
    if (fallback !== undefined && !(error instanceof ApiError)) {
      return fallback;
    }
    if (fallback !== undefined && error instanceof ApiError && error.status !== 401) {
      return fallback;
    }
    throw error;
  }
}

function buildDashboardFallback(locale: Locale): DashboardData {
  if (isChinese(locale)) {
    return {
      repository: 'monorepo://target/payment-gateway',
      codename: '苍龙',
      confidence: '96.4%',
      focus: '反序列化边界 + 鉴权绕过 + 动态链路回放',
      metrics: [
        { id: 'coverage', label: '语义覆盖率', value: '91%', delta: '+12%', tone: 'accent' },
        { id: 'findings', label: '高信号发现', value: '18', delta: '3 个已确认', tone: 'warning' },
        { id: 'breakpoints', label: '断点计划', value: '42', delta: '8 个可直接验证', tone: 'accent' },
        { id: 'containers', label: '沙箱配置', value: '11', delta: '2 个热点环境', tone: 'neutral' },
      ],
      flow: [
        { name: '入口面', count: '124', emphasis: '污点源' },
        { name: '状态漂移', count: '37', emphasis: '鉴权漂移' },
        { name: '危险点', count: '9', emphasis: 'RCE / SSRF' },
        { name: '已证实', count: '3', emphasis: 'PoC 已串联' },
      ],
      capabilities: [
        {
          name: '类人工审计',
          summary: '将语义链路压缩成可读证据，并通过低噪声怀疑排序辅助审计。',
          depth: 'AST + CFG + 调用链评分',
          status: '主通道',
        },
        {
          name: '动态断点编排',
          summary: '将可疑路径直接转换成可调试断点和回放检查点。',
          depth: '运行时探针配方',
          status: '已就绪',
        },
        {
          name: '反编译通道',
          summary: '为 APK/JAR/ELF/PE 逆向、符号恢复与接口恢复预留完整流水线。',
          depth: '多适配器队列',
          status: '排队中',
        },
        {
          name: 'Docker 靶场构建',
          summary: '生成隔离目标环境、夹具密钥、种子流量和利用辅助组件。',
          depth: 'Compose 模板包',
          status: '可用',
        },
      ],
      feed: [
        {
          time: '00:12',
          title: '发现不安全反序列化分支',
          detail: '会话 Cookie 解码流程在缺少稳定白名单证据时进入动态类加载路径。',
          tag: '关键路径',
        },
        {
          time: '00:19',
          title: '已生成断点验证配方',
          detail: '回放计划已将预认证请求体映射到三个调用帧内的危险参数。',
          tag: '动态验证',
        },
        {
          time: '00:27',
          title: 'Docker 沙箱配置已就位',
          detail: '已生成 Redis + App + Mock IdP 组合环境，并注入确定性测试数据。',
          tag: '环境',
        },
      ],
      hotPaths: [
        {
          path: 'src/auth/SessionCodec.java',
          risk: '严重',
          evidence: '不可信字节在自定义标志解包后进入对象重建流程。',
        },
        {
          path: 'pkg/gateway/internal/router.go',
          risk: '高危',
          evidence: '中间件短路分支复用了权限上下文。',
        },
        {
          path: 'services/upload/handler.py',
          risk: '中危',
          evidence: '路径规范化发生在存储后端解析之后。',
        },
      ],
    };
  }

  return {
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
}

function buildMissionsFallback(locale: Locale): Mission[] {
  if (isChinese(locale)) {
    return [
      {
        id: 'm-001',
        name: '网关鉴权漂移',
        target: 'payment-gateway',
        mode: '语义 + 运行时',
        stage: '断点已就绪',
        confidence: '93%',
        findings: 4,
        nextAction: '将调试器挂到反序列化边界',
      },
    ];
  }

  return [
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
  ];
}

function buildLlmStackFallback(locale: Locale): LlmStackData {
  if (isChinese(locale)) {
    return {
      strategy: '将子任务路由到最匹配的模型，综合考虑推理深度、上下文大小、多模态制品、工具调用、部署边界和成本。',
      providers: [],
      blueprints: [],
      runs: [],
    };
  }

  return {
    strategy:
      'Route each subtask to the model best suited for reasoning depth, context size, multimodal artifacts, tool use, deployment boundary, and cost.',
    providers: [],
    blueprints: [],
    runs: [],
  };
}

export function fetchDashboard(locale: Locale) {
  return request<DashboardData>('/api/dashboard', locale, undefined, buildDashboardFallback(locale));
}

export function fetchMissions(locale: Locale) {
  return request<Mission[]>('/api/missions', locale, undefined, buildMissionsFallback(locale));
}

export function fetchLlmStack(locale: Locale) {
  return request<LlmStackData>('/api/llm/stack', locale, undefined, buildLlmStackFallback(locale));
}

export function fetchRepos(locale: Locale) {
  return request<RepoConfig[]>('/api/repos', locale);
}

export function createRepo(
  locale: Locale,
  payload: {
    sourceType?: 'git' | 'local';
    name?: string;
    url?: string;
    branch?: string;
    defaultBaseUrl?: string;
    localPath?: string;
  },
) {
  return request<RepoConfig>('/api/repos', locale, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function syncRepo(locale: Locale, repoId: string) {
  return request<RepoSyncResponse>(`/api/repos/${repoId}/sync`, locale, {
    method: 'POST',
  });
}

export function fetchAudits(locale: Locale) {
  return request<AuditJob[]>('/api/audits', locale);
}

export function fetchAudit(locale: Locale, jobId: string) {
  return request<AuditJob>(`/api/audits/${jobId}`, locale);
}

export function startAudit(locale: Locale, repoId: string) {
  return request<AuditJob>('/api/audits', locale, {
    method: 'POST',
    body: JSON.stringify({ repoId }),
  });
}

export function fetchAuditReport(locale: Locale, jobId: string) {
  return request<AuditReport>(`/api/audits/${jobId}/report`, locale);
}

export { ApiError };
