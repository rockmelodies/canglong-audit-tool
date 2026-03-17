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


class MissionStore:
    def __init__(self) -> None:
        self._missions = [
            Mission(
                id="m-001",
                name="Gateway Auth Drift",
                target="payment-gateway",
                mode="Semantic + Runtime",
                stage="Breakpoint ready",
                confidence="93%",
                findings=4,
                nextAction="Attach debugger to deserialization boundary",
            ),
            Mission(
                id="m-002",
                name="Supply Chain Sandbox",
                target="worker-image",
                mode="Docker deploy",
                stage="Profile staged",
                confidence="88%",
                findings=2,
                nextAction="Boot compose template and replay seed traffic",
            ),
            Mission(
                id="m-003",
                name="Decompiler Sweep",
                target="android-release.apk",
                mode="Reverse engineering",
                stage="Queued",
                confidence="79%",
                findings=0,
                nextAction="Recover symbols and API surfaces",
            ),
        ]

    def list_missions(self) -> list[Mission]:
        return self._missions

    def next_id(self) -> str:
        return f"m-{len(self._missions) + 1:03d}"

    def add_mission(self, mission: Mission) -> Mission:
        self._missions.insert(0, mission)
        return mission


mission_store = MissionStore()


def build_dashboard() -> DashboardResponse:
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
        self._runs = [
            AgentRun(
                id="ar-001",
                agent="Exploit Chain Researcher",
                objective="Trace auth bypass into deserialization sink",
                provider="OpenAI",
                state="Running",
                result="Building exploit precondition matrix and replay prompts.",
            ),
            AgentRun(
                id="ar-002",
                agent="Framework Guard Auditor",
                objective="Check Spring and gateway guard rails for false-positive suppression",
                provider="Anthropic",
                state="Ready",
                result="Guard clauses normalized; 7 noisy paths demoted.",
            ),
            AgentRun(
                id="ar-003",
                agent="Binary Recon Agent",
                objective="Recover API surfaces from uploaded APK",
                provider="Gemini",
                state="Queued",
                result="Waiting for decompile lane and symbol index.",
            ),
        ]

    def list_runs(self) -> list[AgentRun]:
        return self._runs

    def next_id(self) -> str:
        return f"ar-{len(self._runs) + 1:03d}"

    def add_run(self, run: AgentRun) -> AgentRun:
        self._runs.insert(0, run)
        return run


agent_run_store = AgentRunStore()


def build_llm_stack() -> LlmStackResponse:
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
        runs=agent_run_store.list_runs(),
    )
