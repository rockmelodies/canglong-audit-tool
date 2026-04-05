from typing import Literal

from app.models.schemas import (
    AgentBlueprint,
    AgentRun,
    CapabilityItem,
    DashboardResponse,
    EnablementLayer,
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
                MetricCardItem(
                    id="coverage",
                    label="语义覆盖率",
                    value="91%",
                    delta="+12%",
                    tone="accent",
                ),
                MetricCardItem(
                    id="findings",
                    label="高信号发现",
                    value="18",
                    delta="3 个已确认",
                    tone="warning",
                ),
                MetricCardItem(
                    id="breakpoints",
                    label="断点计划",
                    value="42",
                    delta="8 个可直接验证",
                    tone="accent",
                ),
                MetricCardItem(
                    id="containers",
                    label="沙箱配置",
                    value="11",
                    delta="2 个热点环境",
                    tone="neutral",
                ),
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
            MetricCardItem(
                id="coverage",
                label="Semantic Coverage",
                value="91%",
                delta="+12%",
                tone="accent",
            ),
            MetricCardItem(
                id="findings",
                label="High-Signal Findings",
                value="18",
                delta="3 confirmed",
                tone="warning",
            ),
            MetricCardItem(
                id="breakpoints",
                label="Breakpoint Plans",
                value="42",
                delta="8 ready now",
                tone="accent",
            ),
            MetricCardItem(
                id="containers",
                label="Sandbox Profiles",
                value="11",
                delta="2 hot",
                tone="neutral",
            ),
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
                "provider": {"en": "GPT-5.4", "zh-CN": "GPT-5.4"},
                "state": {"en": "Running", "zh-CN": "运行中"},
                "result": {
                    "en": "Expanding the exploit tree with a prompt pack, repo MCP context, and sink-aware tools.",
                    "zh-CN": "正在结合提示词包、仓库 MCP 上下文和 sink 感知工具扩展利用树。",
                },
                "stack": {
                    "en": "GPT-5.4 + Audit Prompt Pack + Repo MCP + Runtime Toolchain",
                    "zh-CN": "GPT-5.4 + 审计提示词包 + 仓库 MCP + 运行时工具链",
                },
            },
            {
                "id": "ar-002",
                "agent": {"en": "Guardrail Reviewer", "zh-CN": "守卫审查 Agent"},
                "objective": {
                    "en": "Review framework guards before promoting auth drift",
                    "zh-CN": "在提升鉴权漂移风险前复核框架守卫",
                },
                "provider": {"en": "Claude Opus 4.6", "zh-CN": "Claude Opus 4.6"},
                "state": {"en": "Ready", "zh-CN": "已完成"},
                "result": {
                    "en": "Long-context review demoted 7 noisy branches after policy checks.",
                    "zh-CN": "长上下文审查结合策略校验后，已降级 7 条高噪声分支。",
                },
                "stack": {
                    "en": "Claude Opus 4.6 + Guard Policy Pack + Diff Review Skill",
                    "zh-CN": "Claude Opus 4.6 + 守卫策略包 + Diff 审查 Skill",
                },
            },
            {
                "id": "ar-003",
                "agent": {"en": "Artifact Recon Agent", "zh-CN": "制品侦察 Agent"},
                "objective": {
                    "en": "Recover API surfaces from uploaded APK screenshots and strings",
                    "zh-CN": "从 APK 截图与字符串中恢复 API 暴露面",
                },
                "provider": {"en": "Gemini 2.5 Pro", "zh-CN": "Gemini 2.5 Pro"},
                "state": {"en": "Queued", "zh-CN": "排队中"},
                "result": {
                    "en": "Waiting for multimodal artifact pack and decompile adapter context.",
                    "zh-CN": "等待多模态制品包和反编译适配器上下文接入。",
                },
                "stack": {
                    "en": "Gemini 2.5 Pro + Artifact Prompt Pack + Decompile Adapter",
                    "zh-CN": "Gemini 2.5 Pro + 制品提示词包 + 反编译适配器",
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
                provider=item["provider"][locale],
                state=item["state"][locale],
                result=item["result"][locale],
                stack=item["stack"][locale],
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
            strategy="默认优先选用能力最强的通用前沿模型，再通过提示词包、MCP、工具链和 Skills 叠加专用能力；只有在长上下文、多模态或私有部署明确占优时才切换模型。",
            providers=[
                ModelProvider(
                    id="gpt54",
                    name="GPT-5.4",
                    category="默认主力通用模型",
                    fit="首选用于代码审计主流程、利用链推演、任务编排和带工具调用的执行。",
                    strengths=["强推理", "工具调用", "结构化输出", "Agent 编排"],
                    deployment="API / Azure / 网关适配",
                    priority="默认",
                    augmentation=["审计提示词包", "仓库 MCP", "运行时工具链", "安全审计 Skills"],
                ),
                ModelProvider(
                    id="opus46",
                    name="Claude Opus 4.6",
                    category="长上下文复核模型",
                    fit="用于大型仓库二次审阅、矛盾分析、守卫复查和长文档收敛。",
                    strengths=["长上下文", "审阅稳定", "复杂文本归纳"],
                    deployment="API / 企业代理",
                    priority="复核",
                    augmentation=["Guard Policy Pack", "Diff Review Skill", "Repo Context MCP"],
                ),
                ModelProvider(
                    id="gemini25pro",
                    name="Gemini 2.5 Pro",
                    category="多模态制品模型",
                    fit="用于反编译制品、截图、流程图和大体量二进制侧信息消化。",
                    strengths=["多模态输入", "宽上下文", "制品理解"],
                    deployment="API / 云工作区",
                    priority="制品",
                    augmentation=["Artifact Prompt Pack", "Decompiler Adapter", "Binary Recon Tooling"],
                ),
            ],
            enablement=[
                EnablementLayer(
                    id="prompt-pack",
                    name="审计提示词包",
                    kind="prompt-pack",
                    summary="把代码审计、误报压制、利用链推演拆成稳定可复用的提示模板。",
                    impact="让通用模型输出更像资深安全工程师，而不是通用问答助手。",
                ),
                EnablementLayer(
                    id="repo-mcp",
                    name="仓库上下文 MCP",
                    kind="mcp",
                    summary="按需暴露代码结构、文件索引、报告历史和环境元数据。",
                    impact="减少上下文丢失和重复贴代码，提高 agent 的定位精度。",
                ),
                EnablementLayer(
                    id="runtime-tools",
                    name="运行时工具链",
                    kind="toolchain",
                    summary="把 grep、AST、HTTP 探测、Docker、diff 等执行能力统一给 agent 调用。",
                    impact="让模型不仅能分析，还能实际收集证据和推进验证。",
                ),
                EnablementLayer(
                    id="security-skills",
                    name="安全审计 Skills",
                    kind="skill-pack",
                    summary="封装常见框架审计、依赖排查、漏洞复核和报告整理流程。",
                    impact="把经验沉淀成标准动作，降低对单次 prompt 的依赖。",
                ),
            ],
            blueprints=[
                AgentBlueprint(
                    name="利用链调研 Agent",
                    purpose="把一条高信号路径扩展成攻击前置条件、横向跳板与验证步骤。",
                    modelStrategy="默认使用 GPT-5.4；若上下文过大或策略冲突较多，再切到 Opus 4.6 复核。",
                    outputs=["利用假设", "回放提示", "验证清单"],
                    status="主用",
                    defaultModel="GPT-5.4",
                    enablement=["审计提示词包", "仓库上下文 MCP", "运行时工具链"],
                ),
                AgentBlueprint(
                    name="误报压制 Agent",
                    purpose="在升级严重等级前交叉检查守卫、净化逻辑、框架约束和部署前提。",
                    modelStrategy="默认使用 Opus 4.6 做长上下文复核，保留 GPT-5.4 作为执行和补证模型。",
                    outputs=["矛盾日志", "降级建议", "证据缺口"],
                    status="主用",
                    defaultModel="Claude Opus 4.6",
                    enablement=["Guard Policy Pack", "Repo Context MCP", "Diff Review Skill"],
                ),
                AgentBlueprint(
                    name="制品侦察 Agent",
                    purpose="把截图、反编译字符串和接口线索整理成可行动的攻击面地图。",
                    modelStrategy="默认使用 Gemini 2.5 Pro，多模态结果再交给 GPT-5.4 整合成审计动作。",
                    outputs=["恢复接口", "密钥线索", "制品风险说明"],
                    status="排队中",
                    defaultModel="Gemini 2.5 Pro",
                    enablement=["Artifact Prompt Pack", "Decompiler Adapter", "Binary Recon Tooling"],
                ),
                AgentBlueprint(
                    name="Docker 验证 Agent",
                    purpose="把审计路径转成可复现环境、验证命令和运行时探针。",
                    modelStrategy="默认使用 GPT-5.4 驱动工具链，并通过 Compose 模板和验证 Skill 降低执行偏差。",
                    outputs=["Compose 方案", "夹具数据", "探针配方"],
                    status="已就绪",
                    defaultModel="GPT-5.4",
                    enablement=["Runtime Toolchain", "Compose Template Pack", "Verification Skill"],
                ),
            ],
            runs=agent_run_store.list_runs(locale),
        )

    return LlmStackResponse(
        strategy=(
            "Default to the strongest general frontier model, then layer prompt packs, MCP context, toolchains, "
            "and skills on top. Only switch models when long-context review, multimodal artifact digestion, or "
            "private deployment has a clear advantage."
        ),
        providers=[
            ModelProvider(
                id="gpt54",
                name="GPT-5.4",
                category="Default general-purpose model",
                fit="Primary choice for code audit orchestration, exploit-chain reasoning, and tool-using execution.",
                strengths=["Strong reasoning", "Tool calling", "Structured outputs", "Agent orchestration"],
                deployment="API / Azure / gateway adapter",
                priority="Default",
                augmentation=["Audit Prompt Pack", "Repository MCP", "Runtime Toolchain", "Security Skills"],
            ),
            ModelProvider(
                id="opus46",
                name="Claude Opus 4.6",
                category="Long-context reviewer",
                fit="Used for second-pass repository review, contradiction analysis, and guardrail validation.",
                strengths=["Long context", "Stable review", "Dense synthesis"],
                deployment="API / enterprise proxy",
                priority="Review",
                augmentation=["Guard Policy Pack", "Diff Review Skill", "Repo Context MCP"],
            ),
            ModelProvider(
                id="gemini25pro",
                name="Gemini 2.5 Pro",
                category="Multimodal artifact model",
                fit="Used for decompile artifacts, screenshots, diagrams, and binary-heavy evidence digestion.",
                strengths=["Multimodal input", "Wide context", "Artifact understanding"],
                deployment="API / cloud workspace",
                priority="Artifact",
                augmentation=["Artifact Prompt Pack", "Decompiler Adapter", "Binary Recon Tooling"],
            ),
        ],
        enablement=[
            EnablementLayer(
                id="prompt-pack",
                name="Audit Prompt Pack",
                kind="prompt-pack",
                summary="Turns audit, false-positive reduction, and exploit-chain expansion into reusable prompt scaffolds.",
                impact="Makes a general model behave more like a disciplined security reviewer than a generic assistant.",
            ),
            EnablementLayer(
                id="repo-mcp",
                name="Repository Context MCP",
                kind="mcp",
                summary="Exposes code structure, file search, report history, and environment metadata on demand.",
                impact="Cuts down repeated context stuffing and improves agent precision inside large repos.",
            ),
            EnablementLayer(
                id="runtime-tools",
                name="Runtime Toolchain",
                kind="toolchain",
                summary="Provides grep, AST, HTTP probing, Docker, and diff execution capabilities to the agent.",
                impact="Lets the model collect evidence and push verification forward instead of only writing analysis.",
            ),
            EnablementLayer(
                id="security-skills",
                name="Security Skills",
                kind="skill-pack",
                summary="Packages framework review, dependency triage, vulnerability validation, and report workflows.",
                impact="Converts team experience into repeatable actions and reduces dependence on one-off prompts.",
            ),
        ],
        blueprints=[
            AgentBlueprint(
                name="Exploit Chain Researcher",
                purpose="Expand one high-signal path into attack preconditions, pivots, and validation steps.",
                modelStrategy="Use GPT-5.4 by default; move to Opus 4.6 only when the review context becomes too large or highly contradictory.",
                outputs=["Exploit hypotheses", "Replay prompts", "Proof checklist"],
                status="Primary",
                defaultModel="GPT-5.4",
                enablement=["Audit Prompt Pack", "Repository MCP", "Runtime Toolchain"],
            ),
            AgentBlueprint(
                name="False-Positive Reducer",
                purpose="Cross-check guards, sanitizers, framework constraints, and deployment assumptions before severity promotion.",
                modelStrategy="Use Opus 4.6 for long-context review and keep GPT-5.4 as the execution and evidence-gathering model.",
                outputs=["Contradiction log", "Severity demotion suggestions", "Evidence gaps"],
                status="Primary",
                defaultModel="Claude Opus 4.6",
                enablement=["Guard Policy Pack", "Repo Context MCP", "Diff Review Skill"],
            ),
            AgentBlueprint(
                name="Artifact Recon Agent",
                purpose="Turn screenshots, decompiled strings, and recovered endpoints into an actionable attack-surface map.",
                modelStrategy="Use Gemini 2.5 Pro for multimodal digestion, then hand off to GPT-5.4 for structured audit actions.",
                outputs=["Recovered endpoints", "Secret hints", "Artifact risk notes"],
                status="Queued",
                defaultModel="Gemini 2.5 Pro",
                enablement=["Artifact Prompt Pack", "Decompiler Adapter", "Binary Recon Tooling"],
            ),
            AgentBlueprint(
                name="Docker Verification Agent",
                purpose="Convert audit paths into reproducible environments, validation commands, and runtime probes.",
                modelStrategy="Use GPT-5.4 with the runtime toolchain and compose templates to reduce execution drift.",
                outputs=["Compose plans", "Fixture data", "Probe recipes"],
                status="Ready",
                defaultModel="GPT-5.4",
                enablement=["Runtime Toolchain", "Compose Template Pack", "Verification Skill"],
            ),
        ],
        runs=agent_run_store.list_runs(locale),
    )
