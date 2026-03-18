from typing import Literal

from app.models.schemas import (
    AgentBlueprint,
    AgentRun,
    CapabilityItem,
    DashboardResponse,
    FeedEvent,
    FlowStage,
    HotPath,
    LlmStackResponse,
    MetricCardItem,
    ModelProvider,
    Mission,
)

Locale = Literal["en", "zh-CN"]


def normalize_locale(lang: str) -> Locale:
    return "zh-CN" if lang.lower().startswith("zh") else "en"


class MissionStore:
    def __init__(self) -> None:
        self._seed_missions = [
            {
                "id": "m-001",
                "name": {"en": "Gateway Auth Drift", "zh-CN": "网关鉴权漂移"},
                "target": "payment-gateway",
                "mode": {"en": "Semantic + Runtime", "zh-CN": "语义 + 运行时"},
                "stage": {"en": "Breakpoint ready", "zh-CN": "断点已就绪"},
                "confidence": "93%",
                "findings": 4,
                "nextAction": {
                    "en": "Attach debugger to deserialization boundary",
                    "zh-CN": "将调试器挂到反序列化边界",
                },
            },
            {
                "id": "m-002",
                "name": {"en": "Supply Chain Sandbox", "zh-CN": "供应链沙箱复现"},
                "target": "worker-image",
                "mode": {"en": "Docker deploy", "zh-CN": "Docker 部署"},
                "stage": {"en": "Profile staged", "zh-CN": "环境已配置"},
                "confidence": "88%",
                "findings": 2,
                "nextAction": {
                    "en": "Boot compose template and replay seed traffic",
                    "zh-CN": "启动 Compose 模板并回放种子流量",
                },
            },
            {
                "id": "m-003",
                "name": {"en": "Decompiler Sweep", "zh-CN": "反编译横向扫描"},
                "target": "android-release.apk",
                "mode": {"en": "Reverse engineering", "zh-CN": "逆向分析"},
                "stage": {"en": "Queued", "zh-CN": "排队中"},
                "confidence": "79%",
                "findings": 0,
                "nextAction": {
                    "en": "Recover symbols and API surfaces",
                    "zh-CN": "恢复符号与 API 暴露面",
                },
            },
        ]
        self._user_missions: list[Mission] = []

    def list_missions(self, lang: str = "en") -> list[Mission]:
        locale = normalize_locale(lang)
        localized = [
            Mission(
                id=item["id"],
                name=item["name"][locale],
                target=item["target"],
                mode=item["mode"][locale],
                stage=item["stage"][locale],
                confidence=item["confidence"],
                findings=item["findings"],
                nextAction=item["nextAction"][locale],
            )
            for item in self._seed_missions
        ]
        return [*self._user_missions, *localized]

    def next_id(self) -> str:
        return f"m-{len(self._seed_missions) + len(self._user_missions) + 1:03d}"

    def add_mission(self, mission: Mission) -> Mission:
        self._user_missions.insert(0, mission)
        return mission


mission_store = MissionStore()


def build_dashboard(lang: str = "en") -> DashboardResponse:
    locale = normalize_locale(lang)

    if locale == "zh-CN":
        return DashboardResponse(
            repository="monorepo://target/payment-gateway",
            codename="苍龙",
            confidence="96.4%",
            focus="反序列化边界 + 鉴权绕过 + 动态链路回放",
            metrics=[
                MetricCardItem(id="coverage", label="语义覆盖率", value="91%", delta="+12%", tone="accent"),
                MetricCardItem(id="findings", label="高信号发现", value="18", delta="3 个已确认", tone="warning"),
                MetricCardItem(id="breakpoints", label="断点计划", value="42", delta="8 个可直接验证", tone="accent"),
                MetricCardItem(id="containers", label="沙箱配置", value="11", delta="2 个热点环境", tone="neutral"),
            ],
            flow=[
                FlowStage(name="入口面", count="124", emphasis="污点源"),
                FlowStage(name="状态漂移", count="37", emphasis="鉴权漂移"),
                FlowStage(name="危险点", count="9", emphasis="RCE / SSRF"),
                FlowStage(name="已证实", count="3", emphasis="PoC 已串联"),
            ],
            capabilities=[
                CapabilityItem(
                    name="类人工审计",
                    summary="将语义链路压缩成可读证据，并通过低噪声怀疑排序辅助审计。",
                    depth="AST + CFG + 调用链评分",
                    status="主通道",
                ),
                CapabilityItem(
                    name="动态断点编排",
                    summary="将可疑路径直接转换成可调试断点和回放检查点。",
                    depth="运行时探针配方",
                    status="已就绪",
                ),
                CapabilityItem(
                    name="反编译通道",
                    summary="为 APK/JAR/ELF/PE 逆向、符号恢复与接口恢复预留完整流水线。",
                    depth="多适配器队列",
                    status="排队中",
                ),
                CapabilityItem(
                    name="Docker 靶场构建",
                    summary="生成隔离目标环境、夹具密钥、种子流量和利用辅助组件。",
                    depth="Compose 模板包",
                    status="可用",
                ),
            ],
            feed=[
                FeedEvent(
                    time="00:12",
                    title="发现不安全反序列化分支",
                    detail="会话 Cookie 解码流程在缺少稳定白名单证据时进入动态类加载路径。",
                    tag="关键路径",
                ),
                FeedEvent(
                    time="00:19",
                    title="已生成断点验证配方",
                    detail="回放计划已将预认证请求体映射到三个调用帧内的危险参数。",
                    tag="动态验证",
                ),
                FeedEvent(
                    time="00:27",
                    title="Docker 沙箱配置已就位",
                    detail="已生成 Redis + App + Mock IdP 组合环境，并注入确定性测试数据。",
                    tag="环境",
                ),
            ],
            hotPaths=[
                HotPath(
                    path="src/auth/SessionCodec.java",
                    risk="严重",
                    evidence="不可信字节在自定义标志解包后进入对象重建流程。",
                ),
                HotPath(
                    path="pkg/gateway/internal/router.go",
                    risk="高危",
                    evidence="中间件短路分支复用了权限上下文。",
                ),
                HotPath(
                    path="services/upload/handler.py",
                    risk="中危",
                    evidence="路径规范化发生在存储后端解析之后。",
                ),
            ],
        )

    return DashboardResponse(
        repository="monorepo://target/payment-gateway",
        codename="Canglong",
        confidence="96.4%",
        focus="Deserialize boundary + auth bypass + dynamic trace replay",
        metrics=[
            MetricCardItem(id="coverage", label="Semantic Coverage", value="91%", delta="+12%", tone="accent"),
            MetricCardItem(id="findings", label="High-Signal Findings", value="18", delta="3 confirmed", tone="warning"),
            MetricCardItem(id="breakpoints", label="Breakpoint Plans", value="42", delta="8 ready now", tone="accent"),
            MetricCardItem(id="containers", label="Sandbox Profiles", value="11", delta="2 hot", tone="neutral"),
        ],
        flow=[
            FlowStage(name="Ingress", count="124", emphasis="taint roots"),
            FlowStage(name="State Drift", count="37", emphasis="auth drift"),
            FlowStage(name="Danger Sink", count="9", emphasis="RCE / SSRF"),
            FlowStage(name="Verified", count="3", emphasis="PoC chained"),
        ],
        capabilities=[
            CapabilityItem(
                name="Human-Like Audit",
                summary="Semantic trace compression, evidence graph, and low-noise suspicion ranking.",
                depth="AST + CFG + call-chain scoring",
                status="Primary",
            ),
            CapabilityItem(
                name="Dynamic Breakpoint Orchestrator",
                summary="Turns suspicious paths into debuggable breakpoints and replay checkpoints.",
                depth="Runtime probe recipes",
                status="Armed",
            ),
            CapabilityItem(
                name="Decompiler Lane",
                summary="Reserved pipeline for APK/JAR/ELF/PE reverse engineering and symbol recovery.",
                depth="Multi-adapter queue",
                status="Queued",
            ),
            CapabilityItem(
                name="Docker Range Builder",
                summary="Builds isolated targets with fixture secrets, seed traffic, and exploit helpers.",
                depth="Compose template packs",
                status="Ready",
            ),
        ],
        feed=[
            FeedEvent(
                time="00:12",
                title="Unsafe deserialization branch surfaced",
                detail="Session cookie decoder reaches dynamic class loading without stable allowlist evidence.",
                tag="Critical path",
            ),
            FeedEvent(
                time="00:19",
                title="Breakpoint recipe generated",
                detail="Replay plan maps pre-auth request body to sink arguments in three frames.",
                tag="Dynamic",
            ),
            FeedEvent(
                time="00:27",
                title="Docker sandbox profile staged",
                detail="Redis + app + mock IdP stack emitted with deterministic seed data.",
                tag="Environment",
            ),
        ],
        hotPaths=[
            HotPath(
                path="src/auth/SessionCodec.java",
                risk="Critical",
                evidence="Untrusted bytes touch object reconstruction after custom flag unwrap.",
            ),
            HotPath(
                path="pkg/gateway/internal/router.go",
                risk="High",
                evidence="Privilege context reused across middleware short-circuit branch.",
            ),
            HotPath(
                path="services/upload/handler.py",
                risk="Medium",
                evidence="Path normalization occurs after storage backend resolution.",
            ),
        ],
    )


class AgentRunStore:
    def __init__(self) -> None:
        self._seed_runs = [
            {
                "id": "ar-001",
                "agent": {"en": "Exploit Chain Researcher", "zh-CN": "利用链调研 Agent"},
                "objective": {
                    "en": "Trace auth bypass into deserialization sink",
                    "zh-CN": "追踪鉴权绕过到反序列化危险点",
                },
                "provider": "OpenAI",
                "state": {"en": "Running", "zh-CN": "运行中"},
                "result": {
                    "en": "Building exploit precondition matrix and replay prompts.",
                    "zh-CN": "正在构建利用前置条件矩阵和回放提示词。",
                },
            },
            {
                "id": "ar-002",
                "agent": {"en": "Framework Guard Auditor", "zh-CN": "框架守卫审计 Agent"},
                "objective": {
                    "en": "Check Spring and gateway guard rails for false-positive suppression",
                    "zh-CN": "核查 Spring 与网关守卫逻辑是否能压制误报",
                },
                "provider": "Anthropic",
                "state": {"en": "Ready", "zh-CN": "已完成"},
                "result": {
                    "en": "Guard clauses normalized; 7 noisy paths demoted.",
                    "zh-CN": "守卫分支已归一化，7 条高噪声路径被降级。",
                },
            },
            {
                "id": "ar-003",
                "agent": {"en": "Binary Recon Agent", "zh-CN": "二进制侦察 Agent"},
                "objective": {
                    "en": "Recover API surfaces from uploaded APK",
                    "zh-CN": "从上传 APK 恢复 API 暴露面",
                },
                "provider": "Gemini",
                "state": {"en": "Queued", "zh-CN": "排队中"},
                "result": {
                    "en": "Waiting for decompile lane and symbol index.",
                    "zh-CN": "等待反编译通道和符号索引完成。",
                },
            },
        ]
        self._user_runs: list[AgentRun] = []

    def list_runs(self, lang: str = "en") -> list[AgentRun]:
        locale = normalize_locale(lang)
        localized = [
            AgentRun(
                id=item["id"],
                agent=item["agent"][locale],
                objective=item["objective"][locale],
                provider=item["provider"],
                state=item["state"][locale],
                result=item["result"][locale],
            )
            for item in self._seed_runs
        ]
        return [*self._user_runs, *localized]

    def next_id(self) -> str:
        return f"ar-{len(self._seed_runs) + len(self._user_runs) + 1:03d}"

    def add_run(self, run: AgentRun) -> AgentRun:
        self._user_runs.insert(0, run)
        return run


agent_run_store = AgentRunStore()


def build_llm_stack(lang: str = "en") -> LlmStackResponse:
    locale = normalize_locale(lang)

    if locale == "zh-CN":
        return LlmStackResponse(
            strategy="将子任务路由到最匹配的模型，综合考虑推理深度、上下文大小、多模态制品、工具调用、部署边界和成本。",
            providers=[
                ModelProvider(
                    id="openai",
                    name="OpenAI",
                    category="推理 + 工具调用",
                    fit="适合利用链推演、Agent 编排和结构化报告生成",
                    strengths=["深度推理", "工具调用", "结构化输出"],
                    deployment="API / Azure / 网关适配",
                ),
                ModelProvider(
                    id="anthropic",
                    name="Anthropic",
                    category="长上下文审阅",
                    fit="适合大型仓库阅读、矛盾分析和高密度代码审阅",
                    strengths=["长上下文", "审阅严谨", "Diff 分析"],
                    deployment="API / 企业代理",
                ),
                ModelProvider(
                    id="gemini",
                    name="Gemini",
                    category="多模态分析",
                    fit="适合反编译制品、流程图、二进制截图和大体量摘要",
                    strengths=["多模态输入", "大上下文", "制品理解"],
                    deployment="API / 云工作区",
                ),
                ModelProvider(
                    id="qwen",
                    name="Qwen",
                    category="开源权重 Agent 通道",
                    fit="适合双语审计和私有化本地执行",
                    strengths=["可自托管", "代码任务", "中英文场景"],
                    deployment="vLLM / SGLang / 自定义网关",
                ),
                ModelProvider(
                    id="deepseek",
                    name="DeepSeek",
                    category="低成本推理",
                    fit="适合漏洞假设横向扩展和大规模初筛",
                    strengths=["推理性价比", "批量初筛", "代码理解"],
                    deployment="API / 兼容网关",
                ),
                ModelProvider(
                    id="selfhosted",
                    name="私有化模型网格",
                    category="敏感代码隔离",
                    fit="适合空气隔离审计与强合规部署",
                    strengths=["私有推理", "适配器可控", "策略隔离"],
                    deployment="Ollama / vLLM / 内部推理服务",
                ),
            ],
            blueprints=[
                AgentBlueprint(
                    name="利用链调研 Agent",
                    purpose="将一条可疑路径扩展成攻击前置条件、横向跳板和验证步骤。",
                    modelStrategy="优先使用强推理模型，必要时回退到低成本批量推理。",
                    outputs=["利用假设", "回放提示", "验证清单"],
                    status="主用",
                ),
                AgentBlueprint(
                    name="误报压制 Agent",
                    purpose="在升级严重等级前，交叉检查框架守卫、净化逻辑与部署约束。",
                    modelStrategy="长上下文审阅模型配合规则校验。",
                    outputs=["矛盾日志", "降级建议", "证据缺口"],
                    status="主用",
                ),
                AgentBlueprint(
                    name="反编译侦察 Agent",
                    purpose="把反编译后的符号、字符串、入口点和 API 暴露面整理成可执行地图。",
                    modelStrategy="多模态模型配合二进制制品适配器。",
                    outputs=["恢复接口", "密钥线索", "依赖风险说明"],
                    status="排队中",
                ),
                AgentBlueprint(
                    name="Docker 靶场规划 Agent",
                    purpose="将可利用路径转成可复现环境配置与运行时探针。",
                    modelStrategy="支持工具调用的模型，接入 Compose 模板注册中心。",
                    outputs=["Compose 方案", "夹具数据", "探针配方"],
                    status="已就绪",
                ),
            ],
            runs=agent_run_store.list_runs(locale),
        )

    return LlmStackResponse(
        strategy=(
            "Route subtasks to the model that best matches reasoning depth, context window, tool use, "
            "multimodal reverse engineering, cost profile, and deployment boundary."
        ),
        providers=[
            ModelProvider(
                id="openai",
                name="OpenAI",
                category="Reasoning + tool use",
                fit="High-confidence exploit reasoning, agent orchestration, report synthesis",
                strengths=["Deep reasoning", "Tool calling", "Structured outputs"],
                deployment="API / Azure / gateway adapter",
            ),
            ModelProvider(
                id="anthropic",
                name="Anthropic",
                category="Long-context review",
                fit="Large codebase reading, policy-heavy review, contradiction analysis",
                strengths=["Long context", "Careful writing", "Diff review"],
                deployment="API / enterprise proxy",
            ),
            ModelProvider(
                id="gemini",
                name="Gemini",
                category="Multimodal analysis",
                fit="Binary screenshots, flow diagrams, decompile artifacts, large repo summarization",
                strengths=["Multimodal input", "Wide context", "Artifact understanding"],
                deployment="API / cloud workspace",
            ),
            ModelProvider(
                id="qwen",
                name="Qwen",
                category="Open-weight agent lane",
                fit="Private deployment, bilingual audit, on-prem tool execution",
                strengths=["Self-hosting", "Code tasks", "Chinese/English usage"],
                deployment="vLLM / SGLang / custom gateway",
            ),
            ModelProvider(
                id="deepseek",
                name="DeepSeek",
                category="Cost-efficient reasoning",
                fit="Wide vulnerability hypothesis sweeps and secondary triage",
                strengths=["Reasoning economy", "Batch triage", "Code comprehension"],
                deployment="API / compatible gateway",
            ),
            ModelProvider(
                id="selfhosted",
                name="Self-hosted Mesh",
                category="Sensitive code isolation",
                fit="Air-gapped source review and data-residency-bound deployments",
                strengths=["Private inference", "Adapter control", "Policy isolation"],
                deployment="Ollama / vLLM / internal serving",
            ),
        ],
        blueprints=[
            AgentBlueprint(
                name="Exploit Chain Researcher",
                purpose="Expand one suspicious path into attack preconditions, pivots, and proof steps.",
                modelStrategy="Reasoning-first provider, fallback to low-cost batch triage model.",
                outputs=["Exploit hypotheses", "Replay prompts", "Proof checklist"],
                status="Primary",
            ),
            AgentBlueprint(
                name="False-Positive Reducer",
                purpose="Cross-check framework guards, sanitizers, and deployment constraints before severity promotion.",
                modelStrategy="Long-context reviewer paired with rules engine.",
                outputs=["Contradiction log", "Severity demotion suggestions", "Evidence gaps"],
                status="Primary",
            ),
            AgentBlueprint(
                name="Decompiler Recon Agent",
                purpose="Digest decompiled symbols, strings, entrypoints, and API surfaces into an actionable map.",
                modelStrategy="Multimodal-capable model with binary artifact adapter.",
                outputs=["Recovered endpoints", "Secret hints", "Library risk notes"],
                status="Queued",
            ),
            AgentBlueprint(
                name="Docker Range Planner",
                purpose="Convert likely exploit paths into reproducible environment profiles and runtime probes.",
                modelStrategy="Tool-using model with compose template registry access.",
                outputs=["Compose plans", "Fixture data", "Probe recipes"],
                status="Ready",
            ),
        ],
        runs=agent_run_store.list_runs(locale),
    )
