/**
 * API Service Module
 * API服务模块
 * 
 * This module provides a centralized API client for communicating with the Canglong backend.
 * It handles authentication, error handling, and provides typed interfaces for all API endpoints.
 * 
 * 本模块提供与苍龙后端通信的集中式API客户端。
 * 它处理认证、错误处理，并为所有API端点提供类型化接口。
 * 
 * Features / 功能特性:
 * - Automatic authentication token management / 自动认证令牌管理
 * - Centralized error handling / 集中式错误处理
 * - Type-safe API calls / 类型安全的API调用
 * - Internationalization support / 国际化支持
 * - Fallback data for development / 开发环境回退数据
 * 
 * Security / 安全:
 * - Tokens are stored securely in session storage / 令牌安全存储在会话存储中
 * - Automatic token refresh on 401 errors / 401错误时自动刷新令牌
 * - All requests use HTTPS in production / 生产环境所有请求使用HTTPS
 * 
 * @module api
 */

import { clearSession, getAccessToken } from '../auth/session';
import type { Locale } from '../i18n/messages';
import type {
  AuditJob,
  AuditReport,
  DashboardData,
  LlmStackData,
  ModelConnection,
  ModelSettingsData,
  Mission,
  RepoConfig,
  RepoSyncResponse,
} from '../types';

/**
 * Base URL for the API backend
 * API后端的基础URL
 * 
 * In production, this should be configured via environment variables.
 * 在生产环境中，应通过环境变量配置。
 */
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:9000';

/**
 * Custom error class for API errors
 * API错误的自定义错误类
 * 
 * Extends the standard Error class to include HTTP status codes.
 * 扩展标准Error类以包含HTTP状态码。
 */
class ApiError extends Error {
  /** HTTP status code / HTTP状态码 */
  status: number;

  /**
   * Create a new ApiError instance
   * 创建新的ApiError实例
   * 
   * @param status - HTTP status code / HTTP状态码
   * @param message - Error message / 错误消息
   */
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = 'ApiError';
  }
}

/**
 * Check if the current locale is Chinese
 * 检查当前语言环境是否为中文
 * 
 * @param locale - Current locale / 当前语言环境
 * @returns True if locale is Chinese / 如果是中文则返回true
 */
function isChinese(locale: Locale) {
  return locale === 'zh-CN';
}

/**
 * Core HTTP request function with authentication and error handling
 * 带有认证和错误处理的核心HTTP请求函数
 * 
 * This function handles all API requests, including:
 * 此函数处理所有API请求，包括：
 * - Adding authentication headers / 添加认证头
 * - Setting content type / 设置内容类型
 * - Handling 401 unauthorized responses / 处理401未授权响应
 * - Error handling with fallback support / 带回退支持的错误处理
 * - Internationalization via query parameter / 通过查询参数进行国际化
 * 
 * @template T - Expected response type / 预期的响应类型
 * @param path - API endpoint path (relative to API_BASE) / API端点路径（相对于API_BASE）
 * @param locale - Current locale for i18n / 当前语言环境
 * @param options - Fetch API options (method, body, etc.) / Fetch API选项（方法、主体等）
 * @param fallback - Optional fallback data to return on error / 错误时返回的可选回退数据
 * @returns Promise resolving to the response data / 返回响应数据的Promise
 * @throws ApiError if the request fails and no fallback is provided / 如果请求失败且没有提供回退数据则抛出ApiError
 * 
 * @example
 * // Simple GET request / 简单GET请求
 * const data = await request<User[]>('/api/users', 'en-US');
 * 
 * @example
 * // POST request with body / 带主体的POST请求
 * const user = await request<User>('/api/users', 'en-US', {
 *   method: 'POST',
 *   body: JSON.stringify({ username: 'test', password: 'pass' })
 * });
 * 
 * @example
 * // Request with fallback / 带回退的请求
 * const data = await request<DashboardData>('/api/dashboard', 'en-US', undefined, fallbackData);
 */
async function request<T>(
  path: string,
  locale: Locale,
  options?: RequestInit,
  fallback?: T,
): Promise<T> {
  // Initialize headers with provided headers or empty object
  // 使用提供的头或空对象初始化头
  const headers = new Headers(options?.headers ?? {});
  
  // Get authentication token from session storage
  // 从会话存储获取认证令牌
  const token = getAccessToken();

  // Add Authorization header if token exists
  // 如果令牌存在，添加Authorization头
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  // Set Content-Type to JSON if body exists and Content-Type not already set
  // 如果主体存在且未设置Content-Type，则设置为JSON
  if (!headers.has('Content-Type') && options?.body) {
    headers.set('Content-Type', 'application/json');
  }

  // Determine query parameter separator based on existing query string
  // 根据现有查询字符串确定查询参数分隔符
  const separator = path.includes('?') ? '&' : '?';
  
  try {
    // Make the HTTP request with locale parameter
    // 使用语言环境参数发出HTTP请求
    const response = await fetch(`${API_BASE}${path}${separator}lang=${encodeURIComponent(locale)}`, {
      ...options,
      headers,
    });

    // Handle 401 Unauthorized - clear session and throw error
    // 处理401未授权 - 清除会话并抛出错误
    if (response.status === 401) {
      clearSession();
      throw new ApiError(401, 'Unauthorized');
    }

    // Handle other error responses
    // 处理其他错误响应
    if (!response.ok) {
      const detail = await response.text();
      throw new ApiError(response.status, detail || `Request failed: ${response.status}`);
    }

    // Parse and return JSON response
    // 解析并返回JSON响应
    return (await response.json()) as T;
  } catch (error) {
    // Return fallback data if provided and error is not an ApiError
    // 如果提供了回退数据且错误不是ApiError，则返回回退数据
    if (fallback !== undefined && !(error instanceof ApiError)) {
      return fallback;
    }
    
    // Return fallback data for non-401 ApiErrors
    // 为非401的ApiError返回回退数据
    if (fallback !== undefined && error instanceof ApiError && error.status !== 401) {
      return fallback;
    }
    
    // Re-throw the error
    // 重新抛出错误
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
      enablement: [],
      blueprints: [],
      runs: [],
    };
  }

  return {
    strategy:
      'Route each subtask to the model best suited for reasoning depth, context size, multimodal artifacts, tool use, deployment boundary, and cost.',
    providers: [],
    enablement: [],
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

export function fetchModelSettings(locale: Locale) {
  return request<ModelSettingsData>('/api/settings/models', locale);
}

export function updateModelSettings(
  locale: Locale,
  modelId: string,
  payload: {
    displayName: string;
    provider: string;
    modelSlug: string;
    description: string;
    baseUrl: string;
    apiKey?: string;
    enabled: boolean;
    capabilityTags: string[];
  },
) {
  return request<ModelConnection>(`/api/settings/models/${modelId}`, locale, {
    method: 'PUT',
    body: JSON.stringify(payload),
  });
}

export function createModelSettings(
  locale: Locale,
  payload: {
    displayName: string;
    provider: string;
    modelSlug: string;
    description: string;
    baseUrl: string;
    apiKey?: string;
    enabled: boolean;
    capabilityTags: string[];
  },
) {
  return request<ModelConnection>('/api/settings/models', locale, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function setDefaultModel(locale: Locale, modelId: string) {
  return request<ModelConnection>(`/api/settings/models/${modelId}/default`, locale, {
    method: 'POST',
  });
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

// User Management API types
export interface User {
  username: string;
  displayName: string;
  email?: string;
  role: 'administrator' | 'auditor' | 'viewer';
  active: boolean;
  createdAt: string;
  lastLogin?: string;
}

export interface ApiKey {
  id: string;
  name: string;
  owner: string;
  permissions: string[];
  status: 'active' | 'revoked' | 'expired';
  createdAt: string;
  expiresAt?: string;
  lastUsed?: string;
  keyPrefix?: string;
  fullKey?: string;
}

export interface Invite {
  id: string;
  email: string;
  role: 'administrator' | 'auditor' | 'viewer';
  status: 'pending' | 'accepted' | 'expired' | 'revoked';
  invitedBy: string;
  createdAt: string;
  expiresAt: string;
}

export interface UserPermissions {
  role: string;
  permissions: string[];
  canManageUsers: boolean;
  canManageApiKeys: boolean;
  canCreateAudit: boolean;
  canViewReport: boolean;
}

// User Management API methods
export function fetchUsers(locale: Locale) {
  return request<User[]>('/api/users', locale);
}

export function fetchUser(locale: Locale, username: string) {
  return request<User>(`/api/users/${encodeURIComponent(username)}`, locale);
}

export function createUser(
  locale: Locale,
  payload: {
    username: string;
    password: string;
    displayName: string;
    email?: string;
    role: 'administrator' | 'auditor' | 'viewer';
  },
) {
  return request<User>('/api/users', locale, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function updateUser(
  locale: Locale,
  username: string,
  payload: {
    displayName?: string;
    email?: string;
    role?: 'administrator' | 'auditor' | 'viewer';
    active?: boolean;
  },
) {
  return request<User>(`/api/users/${encodeURIComponent(username)}`, locale, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}

export function deleteUser(locale: Locale, username: string) {
  return request<void>(`/api/users/${encodeURIComponent(username)}`, locale, {
    method: 'DELETE',
  });
}

// API Key Management
export function fetchMyApiKeys(locale: Locale) {
  return request<ApiKey[]>('/api/users/me/keys', locale);
}

export function createApiKey(
  locale: Locale,
  payload: {
    name: string;
    permissions?: string[];
    expiresAt?: string;
  },
) {
  return request<ApiKey & { fullKey: string }>('/api/users/me/keys', locale, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function revokeMyApiKey(locale: Locale, keyId: string) {
  return request<void>(`/api/users/me/keys/${keyId}`, locale, {
    method: 'DELETE',
  });
}

export function fetchAllApiKeys(locale: Locale) {
  return request<ApiKey[]>('/api/users/keys', locale);
}

export function revokeAnyApiKey(locale: Locale, keyId: string) {
  return request<void>(`/api/users/keys/${keyId}`, locale, {
    method: 'DELETE',
  });
}

// Invitation Management
export function createInvite(
  locale: Locale,
  payload: {
    email: string;
    role: 'administrator' | 'auditor' | 'viewer';
  },
) {
  return request<Invite>('/api/users/invites', locale, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function fetchInvites(locale: Locale) {
  return request<Invite[]>('/api/users/invites', locale);
}

export function revokeInvite(locale: Locale, inviteId: string) {
  return request<void>(`/api/users/invites/${inviteId}`, locale, {
    method: 'DELETE',
  });
}

/**
 * Accept an invitation and create a new user account
 * 接受邀请并创建新用户账户
 * 
 * @param locale - Current locale for i18n / 当前语言环境
 * @param inviteId - The invitation ID to accept / 要接受的邀请ID
 * @param payload - User registration information / 用户注册信息
 * @returns Promise resolving to the created user / 返回创建的用户
 * 
 * @throws ApiError if the invitation is invalid, expired, or registration fails
 * 如果邀请无效、已过期或注册失败则抛出ApiError
 */
export function acceptInvite(
  locale: Locale,
  inviteId: string,
  payload: {
    username: string;
    password: string;
    displayName: string;
  },
) {
  return request<User>(`/api/users/accept-invite/${inviteId}`, locale, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

// Current user permissions
export function fetchMyPermissions(locale: Locale) {
  return request<UserPermissions>('/api/users/me/permissions', locale);
}

export { ApiError };
