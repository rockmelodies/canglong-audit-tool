from __future__ import annotations

import ast
import json
import os
import re
import socket
import subprocess
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import uuid4
from xml.etree import ElementTree

from fastapi import HTTPException, status

from app.models.schemas import (
    ApplicabilityCheck,
    AuditJob,
    AuditReport,
    AuditStage,
    AuditSummary,
    DependencyEvidence,
    DockerVerification,
    EndpointRecord,
    EnvironmentFingerprint,
    ExploitChainCandidate,
    FalsePositiveControl,
    InterfaceTestPlan,
    VulnerabilityFinding,
)
from app.services.repo_manager import repo_store, sync_repo, utc_now


IGNORED_DIRS = {
    ".git",
    ".idea",
    ".venv",
    ".pytest_cache",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "target",
    "vendor",
    "venv",
}

INTERESTING_SUFFIXES = {
    ".go",
    ".gradle",
    ".java",
    ".js",
    ".json",
    ".jsx",
    ".kt",
    ".kts",
    ".php",
    ".properties",
    ".py",
    ".ts",
    ".tsx",
    ".xml",
    ".yaml",
    ".yml",
}

IMPORTANT_FILENAMES = {
    "Dockerfile",
    "compose.yml",
    "compose.yaml",
    "docker-compose.yml",
    "docker-compose.yaml",
    "go.mod",
    "package-lock.json",
    "package.json",
    "pom.xml",
    "requirements.txt",
    "settings.gradle",
    "settings.gradle.kts",
}

PYTHON_HTTP_METHODS = {"get", "post", "put", "patch", "delete"}

JS_ROUTE_PATTERN = re.compile(
    r"""(?:app|router)\.(get|post|put|patch|delete)\(\s*['"`]([^'"`]+)['"`]\s*,\s*([A-Za-z0-9_$.]+)""",
    re.IGNORECASE,
)
JAVA_ROUTE_PATTERN = re.compile(
    r"""@(?P<annotation>GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping|RequestMapping)\((?P<args>[^)]*)\)\s*(?:public|protected|private)?\s+[^\s]+\s+(?P<handler>[A-Za-z0-9_]+)\s*\(""",
    re.MULTILINE,
)


@dataclass(frozen=True)
class FindingMatch:
    title_en: str
    title_zh: str
    category: str
    severity: str
    summary_en: str
    summary_zh: str
    pattern: re.Pattern[str]
    chain_en: list[str]
    chain_zh: list[str]


FINDING_RULES = [
    FindingMatch(
        title_en="Potential command execution sink",
        title_zh="疑似命令执行落点",
        category="command-execution",
        severity="critical",
        summary_en="User-controlled data may reach an operating-system command invocation.",
        summary_zh="用户可控数据可能流入操作系统命令执行位置。",
        pattern=re.compile(
            r"(subprocess\.(run|Popen|call)\([^)]*shell\s*=\s*True|os\.system\(|Runtime\.getRuntime\(\)\.exec\(|ProcessBuilder\s*\(|exec\s*\(|system\s*\(|passthru\s*\(|shell_exec\s*\()"
        ),
        chain_en=["Ingress parameter", "Unsafe shell bridge", "Command sink"],
        chain_zh=["入口参数", "危险 Shell 桥接", "命令执行落点"],
    ),
    FindingMatch(
        title_en="Potential SQL injection",
        title_zh="疑似SQL注入",
        category="sql-injection",
        severity="critical",
        summary_en="User input may be concatenated into SQL queries without proper parameterization.",
        summary_zh="用户输入可能未经参数化处理直接拼接到SQL查询中。",
        pattern=re.compile(
            r"(execute\s*\(\s*['\"]\s*\+|query\s*\(\s*['\"]\s*\+|\.execute\s*\([^)]*\+|\.query\s*\([^)]*\+|SELECT.*FROM.*WHERE.*\+|INSERT.*INTO.*VALUES.*\+|UPDATE.*SET.*\+|DELETE.*FROM.*\+)"
        ),
        chain_en=["User input", "String concatenation", "SQL query"],
        chain_zh=["用户输入", "字符串拼接", "SQL查询"],
    ),
    FindingMatch(
        title_en="Potential XSS vulnerability",
        title_zh="疑似XSS漏洞",
        category="xss",
        severity="high",
        summary_en="Unsanitized user input may be rendered directly into web pages.",
        summary_zh="未经净化的用户输入可能直接渲染到网页中。",
        pattern=re.compile(
            r"(innerHTML\s*=|outerHTML\s*=|document\.write\s*\(|\.html\s*\(|dangerouslySetInnerHTML|v-html\s*=|ng-bind-html\s*=)"
        ),
        chain_en=["User input", "Direct rendering", "Browser execution"],
        chain_zh=["用户输入", "直接渲染", "浏览器执行"],
    ),
    FindingMatch(
        title_en="Potential SSRF vulnerability",
        title_zh="疑似SSRF漏洞",
        category="ssrf",
        severity="high",
        summary_en="User-controlled URLs may be fetched by the server without proper validation.",
        summary_zh="用户可控的URL可能被服务器直接请求而未经验证。",
        pattern=re.compile(
            r"(requests\.(get|post|put|delete|patch)\(|urllib\.request\.|urllib\.urlopen\(|fetch\s*\(|http\.get\s*\(|axios\.(get|post|put|delete|patch)\(|HttpClient\.request\s*\()"
        ),
        chain_en=["User URL", "Server-side request", "Internal network access"],
        chain_zh=["用户URL", "服务端请求", "内网访问"],
    ),
    FindingMatch(
        title_en="Potential path traversal",
        title_zh="疑似路径遍历",
        category="path-traversal",
        severity="high",
        summary_en="User input may be used to access files outside the intended directory.",
        summary_zh="用户输入可能被用于访问预期目录之外的文件。",
        pattern=re.compile(
            r"(open\s*\([^)]*\+|readfile\s*\([^)]*\+|file_get_contents\s*\([^)]*\+|include\s*\([^)]*\+|require\s*\([^)]*\+|File\s*\([^)]*\+|Path\s*\([^)]*\+)"
        ),
        chain_en=["User input", "File path", "Arbitrary file access"],
        chain_zh=["用户输入", "文件路径", "任意文件访问"],
    ),
    FindingMatch(
        title_en="Potential insecure deserialization",
        title_zh="疑似不安全反序列化",
        category="insecure-deserialization",
        severity="critical",
        summary_en="Serialized or dynamic type input appears to be reconstructed without strong safety controls.",
        summary_zh="序列化或动态类型输入疑似在缺少强约束的情况下被重建。",
        pattern=re.compile(r"(pickle\.loads\(|yaml\.load\(|ObjectInputStream|readObject\(|enableDefaultTyping|\.deserialize\s*\(|JSON\.parseObject\s*\()"),
        chain_en=["Untrusted payload", "Deserializer", "Reachable gadget or object graph"],
        chain_zh=["不可信载荷", "反序列化器", "可达 Gadget 或对象图"],
    ),
    FindingMatch(
        title_en="Potential weak crypto usage",
        title_zh="疑似弱加密使用",
        category="weak-crypto",
        severity="medium",
        summary_en="Weak or legacy hash primitives are present in security-sensitive code.",
        summary_zh="安全敏感路径中出现弱哈希或过时加密原语。",
        pattern=re.compile(r"(md5\(|sha1\(|MessageDigest\.getInstance\(\"(MD5|SHA-1)\"\)|hash\s*\(\s*['\"]md5|hash\s*\(\s*['\"]sha1)"),
        chain_en=["Credential material", "Weak digest", "Collision or downgrade risk"],
        chain_zh=["凭证材料", "弱摘要算法", "碰撞或降级风险"],
    ),
    FindingMatch(
        title_en="Potential hardcoded credentials",
        title_zh="疑似硬编码凭证",
        category="hardcoded-credentials",
        severity="high",
        summary_en="Credentials or API keys may be hardcoded in source files.",
        summary_zh="凭证或API密钥可能硬编码在源文件中。",
        pattern=re.compile(
            r"(password\s*=\s*['\"][^'\"]{8,}['\"]|api_key\s*=\s*['\"][^'\"]{20,}['\"]|secret\s*=\s*['\"][^'\"]{16,}['\"]|token\s*=\s*['\"][^'\"]{20,}['\"])"
        ),
        chain_en=["Hardcoded secret", "Source code", "Credential exposure"],
        chain_zh=["硬编码密钥", "源代码", "凭证泄露"],
    ),
    FindingMatch(
        title_en="Potential insecure random number generation",
        title_zh="疑似不安全的随机数生成",
        category="insecure-random",
        severity="medium",
        summary_en="Weak random number generators may be used for security-sensitive operations.",
        summary_zh="安全敏感操作中可能使用了弱随机数生成器。",
        pattern=re.compile(
            r"(Math\.random\s*\(|random\.random\s*\(|rand\s*\(\)|mt_rand\s*\(\)|Random\s*\(\))"
        ),
        chain_en=["Weak RNG", "Security context", "Predictable values"],
        chain_zh=["弱随机数生成器", "安全上下文", "可预测值"],
    ),
    FindingMatch(
        title_en="Potential auth bypass branch",
        title_zh="疑似认证绕过分支",
        category="auth-bypass",
        severity="high",
        summary_en="A route or security branch appears to allow unauthenticated access.",
        summary_zh="路由或安全分支疑似允许未认证访问。",
        pattern=re.compile(r"(@PermitAll|permitAll\(|skipAuth|AllowAnonymous|anonymousAccess|@NoAuth|bypassAuth)"),
        chain_en=["Ingress route", "Guard exception", "Protected capability exposed"],
        chain_zh=["入口路由", "鉴权例外", "受保护能力暴露"],
    ),
    FindingMatch(
        title_en="Potential information disclosure",
        title_zh="疑似信息泄露",
        category="info-disclosure",
        severity="medium",
        summary_en="Sensitive information may be exposed through error messages or debug output.",
        summary_zh="敏感信息可能通过错误消息或调试输出泄露。",
        pattern=re.compile(
            r"(print\s*\([^)]*exception|console\.log\s*\([^)]*error|console\.error\s*\(|debug\s*=\s*True|DEBUG\s*=\s*True|stacktrace|traceback\.print_exc)"
        ),
        chain_en=["Error output", "Sensitive data", "Information leak"],
        chain_zh=["错误输出", "敏感数据", "信息泄露"],
    ),
    FindingMatch(
        title_en="Potential insecure file upload",
        title_zh="疑似不安全的文件上传",
        category="insecure-upload",
        severity="high",
        summary_en="File uploads may not have proper validation on file type or content.",
        summary_zh="文件上传可能缺少对文件类型或内容的适当验证。",
        pattern=re.compile(
            r"(upload\s*\(|save_uploaded_file|FileUpload|@PostMapping.*upload|multipart/form-data)"
        ),
        chain_en=["File upload", "Missing validation", "Arbitrary file execution"],
        chain_zh=["文件上传", "缺少验证", "任意文件执行"],
    ),
]


def normalize_locale(lang: str) -> str:
    return "zh-CN" if lang.lower().startswith("zh") else "en"


def localize(locale: str, en: str, zh: str) -> str:
    return zh if locale == "zh-CN" else en


def read_text(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "gb18030", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="ignore")


def relative_path(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve())).replace("\\", "/")
    except ValueError:
        return path.name


def format_exception_message(exc: Exception) -> str:
    return str(exc) or exc.__class__.__name__


def iter_repository_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for current_root, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in IGNORED_DIRS]
        current = Path(current_root)
        for filename in filenames:
            candidate = current / filename
            if filename in IMPORTANT_FILENAMES or candidate.suffix.lower() in INTERESTING_SUFFIXES:
                files.append(candidate)
    return files


def guess_language(path: Path) -> str | None:
    suffix = path.suffix.lower()
    if suffix == ".py":
        return "Python"
    if suffix in {".js", ".jsx", ".ts", ".tsx"}:
        return "JavaScript/TypeScript"
    if suffix in {".java", ".kt", ".kts", ".gradle"}:
        return "Java/Kotlin"
    if suffix == ".go":
        return "Go"
    if suffix == ".php":
        return "PHP"
    if path.name in {"package.json", "package-lock.json"}:
        return "JavaScript/TypeScript"
    if path.name == "requirements.txt":
        return "Python"
    if path.name in {"pom.xml", "settings.gradle", "settings.gradle.kts"}:
        return "Java/Kotlin"
    if path.name == "go.mod":
        return "Go"
    return None


def build_environment_fingerprint(root: Path, files: list[Path]) -> EnvironmentFingerprint:
    languages: set[str] = set()
    frameworks: set[str] = set()
    build_files: list[str] = []
    runtime_hints: set[str] = set()
    packaging: set[str] = set()
    java_version_hint: str | None = None
    servlet_namespace: str | None = None

    for path in files:
        relative = relative_path(root, path)
        language = guess_language(path)
        if language:
            languages.add(language)

        if path.name in IMPORTANT_FILENAMES:
            build_files.append(relative)

        text = ""
        if path.suffix.lower() in {".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".kt", ".kts", ".xml", ".json", ".yml", ".yaml", ".properties", ".gradle"} or path.name in IMPORTANT_FILENAMES:
            text = read_text(path)

        lowered = text.lower()
        if "fastapi" in lowered:
            frameworks.add("FastAPI")
        if "flask" in lowered:
            frameworks.add("Flask")
        if "springboot" in lowered or "@restcontroller" in lowered or "@requestmapping" in lowered:
            frameworks.add("Spring Boot")
        if "@path(" in lowered or "javax.ws.rs" in lowered or "jakarta.ws.rs" in lowered:
            frameworks.add("JAX-RS")
        if "org.apache.shiro" in lowered or "shirofilterfactorybean" in lowered:
            frameworks.add("Apache Shiro")
        if "dubbo" in lowered:
            frameworks.add("Apache Dubbo")
        if "mybatis" in lowered:
            frameworks.add("MyBatis")
        if "struts" in lowered:
            frameworks.add("Apache Struts")
        if "hessian" in lowered:
            frameworks.add("Hessian")
        if "express(" in lowered or "express." in lowered:
            frameworks.add("Express")
        if '"github.com/gin-gonic/gin"' in lowered or "gin.default(" in lowered:
            frameworks.add("Gin")
        if "django" in lowered:
            frameworks.add("Django")
        if "laravel" in lowered:
            frameworks.add("Laravel")

        if "jakarta.servlet" in text:
            servlet_namespace = "jakarta.servlet"
        elif "javax.servlet" in text and servlet_namespace is None:
            servlet_namespace = "javax.servlet"

        if java_version_hint is None:
            match = re.search(r"<java\.version>([^<]+)</java\.version>", text)
            if match:
                java_version_hint = match.group(1).strip()
            else:
                match = re.search(r"sourceCompatibility\s*=\s*['\"]?([^'\"\n]+)", text)
                if match:
                    java_version_hint = match.group(1).strip()

        if path.name == "Dockerfile":
            runtime_hints.add("Dockerfile present")
            packaging.add("container")
        if path.name in {"docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"}:
            runtime_hints.add("Compose profile present")
            packaging.add("container")
        if path.suffix.lower() in {".jar", ".war"}:
            packaging.add(path.suffix.lower().removeprefix("."))
        if path.suffix.lower() == ".apk":
            packaging.add("apk")
        if path.name in {"pom.xml", "build.gradle", "build.gradle.kts"}:
            runtime_hints.add("Java build manifest present")

    return EnvironmentFingerprint(
        languages=sorted(languages),
        frameworks=sorted(frameworks),
        buildFiles=build_files[:24],
        javaVersionHint=java_version_hint,
        servletNamespace=servlet_namespace,
        runtimeHints=sorted(runtime_hints),
        packaging=sorted(packaging),
    )


def _clean_dependency_name(raw: str) -> str:
    return raw.strip().strip('"').strip("'")


def collect_dependencies(root: Path, files: list[Path]) -> list[DependencyEvidence]:
    dependencies: list[DependencyEvidence] = []
    seen: set[tuple[str, str, str]] = set()

    def append_dependency(item: DependencyEvidence) -> None:
        key = (item.ecosystem, item.name, item.sourceFile)
        if key in seen:
            return
        seen.add(key)
        dependencies.append(item)

    for path in files:
        relative = relative_path(root, path)
        if path.name == "requirements.txt":
            for line in read_text(path).splitlines():
                candidate = line.strip()
                if not candidate or candidate.startswith("#"):
                    continue
                name = re.split(r"[<>=!~\[]", candidate, maxsplit=1)[0].strip()
                version_match = re.search(r"(==|>=|<=|~=|!=)\s*([A-Za-z0-9._-]+)", candidate)
                append_dependency(
                    DependencyEvidence(
                        ecosystem="pip",
                        name=name,
                        version=version_match.group(2) if version_match else None,
                        sourceFile=relative,
                        scope="runtime",
                    )
                )
        elif path.name == "package.json":
            try:
                package_json = json.loads(read_text(path))
            except json.JSONDecodeError:
                continue
            for scope in ("dependencies", "devDependencies"):
                for name, version in (package_json.get(scope) or {}).items():
                    append_dependency(
                        DependencyEvidence(
                            ecosystem="npm",
                            name=_clean_dependency_name(name),
                            version=_clean_dependency_name(str(version)),
                            sourceFile=relative,
                            scope="runtime" if scope == "dependencies" else "development",
                        )
                    )
        elif path.name == "pom.xml":
            try:
                tree = ElementTree.fromstring(read_text(path))
            except ElementTree.ParseError:
                continue
            for dependency in tree.findall(".//{*}dependency"):
                group_id = (dependency.findtext("{*}groupId") or "").strip()
                artifact = dependency.findtext("{*}artifactId")
                if not artifact:
                    continue
                append_dependency(
                    DependencyEvidence(
                        ecosystem="maven",
                        name=f"{group_id}:{artifact.strip()}" if group_id else artifact.strip(),
                        version=(dependency.findtext("{*}version") or "").strip() or None,
                        sourceFile=relative,
                        scope=(dependency.findtext("{*}scope") or "").strip() or "runtime",
                    )
                )
        elif path.name in {"build.gradle", "build.gradle.kts"}:
            text = read_text(path)
            for scope, dependency_spec in re.findall(
                r"(implementation|api|compileOnly|runtimeOnly|testImplementation|testRuntimeOnly)\s*\(?\s*['\"]([^'\"]+)['\"]",
                text,
            ):
                parts = dependency_spec.split(":")
                if len(parts) >= 2:
                    name = f"{parts[0]}:{parts[1]}"
                    version = parts[2] if len(parts) >= 3 else None
                else:
                    name = dependency_spec
                    version = None
                append_dependency(
                    DependencyEvidence(
                        ecosystem="gradle",
                        name=name,
                        version=version,
                        sourceFile=relative,
                        scope=scope,
                    )
                )
        elif path.name == "go.mod":
            for line in read_text(path).splitlines():
                stripped = line.strip()
                if stripped.startswith("require "):
                    parts = stripped.split()
                    if len(parts) >= 3:
                        append_dependency(
                            DependencyEvidence(
                                ecosystem="go",
                                name=parts[1],
                                version=parts[2],
                                sourceFile=relative,
                                scope="runtime",
                            )
                        )

    return dependencies[:80]


def _call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _extract_python_flow(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    calls: list[str] = []
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            name = _call_name(child.func)
            if name and name not in calls:
                calls.append(name)
        if len(calls) >= 4:
            break
    return calls


def _extract_python_router_prefixes(tree: ast.AST) -> dict[str, str]:
    prefixes: dict[str, str] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.Call):
            continue
        callee = _call_name(node.value.func)
        if not callee or not callee.endswith("APIRouter"):
            continue
        prefix = "/"
        for keyword in node.value.keywords:
            if keyword.arg == "prefix" and isinstance(keyword.value, ast.Constant) and isinstance(keyword.value.value, str):
                prefix = keyword.value.value or "/"
                break
        for target in node.targets:
            if isinstance(target, ast.Name):
                prefixes[target.id] = prefix
    return prefixes


def _join_route_path(prefix: str, path: str) -> str:
    normalized_prefix = "" if prefix in {"", "/"} else prefix.rstrip("/")
    normalized_path = path or "/"
    normalized_path = normalized_path if normalized_path.startswith("/") else f"/{normalized_path}"
    joined = f"{normalized_prefix}{normalized_path}" if normalized_prefix else normalized_path
    return joined or "/"


def _parse_python_route(decoration: ast.AST, router_prefixes: dict[str, str]) -> tuple[str, str] | None:
    if not isinstance(decoration, ast.Call) or not isinstance(decoration.func, ast.Attribute):
        return None

    attr = decoration.func.attr.lower()
    method: str | None = None
    path = "/"

    if attr in PYTHON_HTTP_METHODS:
        method = attr.upper()
    elif attr == "route":
        methods_kw = next(
            (
                keyword
                for keyword in decoration.keywords
                if keyword.arg == "methods" and isinstance(keyword.value, (ast.List, ast.Tuple))
            ),
            None,
        )
        if methods_kw and isinstance(methods_kw.value, (ast.List, ast.Tuple)) and methods_kw.value.elts:
            first_method = methods_kw.value.elts[0]
            if isinstance(first_method, ast.Constant) and isinstance(first_method.value, str):
                method = first_method.value.upper()
    else:
        return None

    if decoration.args and isinstance(decoration.args[0], ast.Constant) and isinstance(decoration.args[0].value, str):
        path = decoration.args[0].value

    router_prefix = ""
    if isinstance(decoration.func.value, ast.Name):
        router_prefix = router_prefixes.get(decoration.func.value.id, "")

    return (method or "GET", _join_route_path(router_prefix, path))


def discover_endpoints(root: Path, files: list[Path]) -> list[EndpointRecord]:
    endpoints: list[EndpointRecord] = []
    seen: set[tuple[str, str, str]] = set()

    def append_endpoint(item: EndpointRecord) -> None:
        key = (item.method, item.path, item.file)
        if key in seen:
            return
        seen.add(key)
        endpoints.append(item)

    for path in files:
        relative = relative_path(root, path)
        suffix = path.suffix.lower()
        if suffix == ".py":
            text = read_text(path)
            try:
                tree = ast.parse(text)
            except SyntaxError:
                continue
            router_prefixes = _extract_python_router_prefixes(tree)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for decoration in node.decorator_list:
                        parsed = _parse_python_route(decoration, router_prefixes)
                        if not parsed:
                            continue
                        method, endpoint_path = parsed
                        append_endpoint(
                            EndpointRecord(
                                method=method,
                                path=endpoint_path,
                                framework="Python",
                                handler=node.name,
                                file=relative,
                                flow=_extract_python_flow(node),
                            )
                        )
        elif suffix in {".js", ".jsx", ".ts", ".tsx"}:
            text = read_text(path)
            for match in JS_ROUTE_PATTERN.finditer(text):
                append_endpoint(
                    EndpointRecord(
                        method=match.group(1).upper(),
                        path=match.group(2),
                        framework="Express",
                        handler=match.group(3).split(".")[-1],
                        file=relative,
                        flow=[match.group(3).split(".")[-1]],
                    )
                )
        elif suffix in {".java", ".kt"}:
            text = read_text(path)
            base_path = ""
            class_mapping = re.search(r"@RequestMapping\(([^)]*)\)\s*public\s+class", text)
            if class_mapping:
                path_match = re.search(r"['\"]([^'\"]+)['\"]", class_mapping.group(1))
                if path_match:
                    base_path = path_match.group(1)
            for match in JAVA_ROUTE_PATTERN.finditer(text):
                annotation = match.group("annotation")
                args = match.group("args")
                path_match = re.search(r"['\"]([^'\"]+)['\"]", args)
                endpoint_path = f"{base_path}{path_match.group(1) if path_match else ''}" or "/"
                if annotation == "RequestMapping":
                    method_match = re.search(r"RequestMethod\.(GET|POST|PUT|PATCH|DELETE)", args)
                    method = method_match.group(1) if method_match else "GET"
                else:
                    method = annotation.removesuffix("Mapping").upper()
                append_endpoint(
                    EndpointRecord(
                        method=method,
                        path=endpoint_path,
                        framework="Spring",
                        handler=match.group("handler"),
                        file=relative,
                        flow=[match.group("handler")],
                    )
                )

    return endpoints[:120]


def scan_findings(root: Path, files: list[Path], locale: str) -> list[VulnerabilityFinding]:
    findings: list[VulnerabilityFinding] = []

    for path in files:
        if path.suffix.lower() not in {".go", ".java", ".js", ".jsx", ".kt", ".kts", ".php", ".py", ".ts", ".tsx"}:
            continue

        text = read_text(path)
        relative = relative_path(root, path)
        for rule in FINDING_RULES:
            match = rule.pattern.search(text)
            if not match:
                continue

            line_number = text.count("\n", 0, match.start()) + 1
            findings.append(
                VulnerabilityFinding(
                    id=f"finding-{uuid4().hex[:8]}",
                    title=localize(locale, rule.title_en, rule.title_zh),
                    category=rule.category,
                    severity=rule.severity,  # type: ignore[arg-type]
                    file=relative,
                    line=line_number,
                    summary=localize(locale, rule.summary_en, rule.summary_zh),
                    evidence=(match.group(0)[:180] + "...") if len(match.group(0)) > 180 else match.group(0),
                    chain=rule.chain_zh if locale == "zh-CN" else rule.chain_en,
                )
            )

        if path.suffix.lower() in {".java", ".kt"}:
            findings.extend(scan_java_findings(text, relative, locale))

    severity_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    deduped: list[VulnerabilityFinding] = []
    seen: set[tuple[str, int, str]] = set()
    for finding in findings:
        key = (finding.file, finding.line, finding.category)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(finding)
    deduped.sort(key=lambda item: (severity_rank[item.severity], item.file, item.line))
    return deduped[:60]


def scan_java_findings(text: str, relative: str, locale: str) -> list[VulnerabilityFinding]:
    java_rules = [
        (
            "jndi-injection",
            "high",
            "Potential JNDI lookup chain",
            "疑似 JNDI 查询链",
            "JNDI lookups can bridge attacker-controlled names into remote naming or local gadget resolution.",
            "JNDI 查询可能将攻击者可控名称桥接到远程命名或本地 Gadget 解析。",
            re.compile(r"(InitialContext\s*\(\)|JndiTemplate|JndiManager)[^;\n]{0,120}\.lookup\s*\("),
            ["Ingress parameter", "JNDI lookup", "Remote naming resolution"],
            ["入口参数", "JNDI 查询", "远程命名解析"],
        ),
        (
            "fastjson-autotype",
            "critical",
            "Potential Fastjson AutoType chain",
            "疑似 Fastjson AutoType 链",
            "Fastjson auto type or unsafe parse paths can unlock gadget materialization.",
            "Fastjson AutoType 或不安全解析路径可能触发 Gadget 实例化。",
            re.compile(
                r"(ParserConfig\.getGlobalInstance\(\)\.setAutoTypeSupport\s*\(\s*true\s*\)|Feature\.SupportAutoType|JSON\.parse(Object|Array)\s*\()"
            ),
            ["Untrusted JSON", "Fastjson parse", "AutoType or gadget materialization"],
            ["不可信 JSON", "Fastjson 解析", "AutoType 或 Gadget 实例化"],
        ),
        (
            "hessian-deserialization",
            "high",
            "Potential Hessian or Dubbo deserialization chain",
            "疑似 Hessian 或 Dubbo 反序列化链",
            "Hessian-based input handling can deserialize attacker-controlled object graphs.",
            "基于 Hessian 的输入处理可能反序列化攻击者可控对象图。",
            re.compile(r"(Hessian(Input|2Input)|HessianServiceExporter|HessianProxyFactory|DubboCodec|DecodeableRpcInvocation)"),
            ["Binary payload", "Hessian decoder", "Reachable object graph"],
            ["二进制载荷", "Hessian 解码器", "可达对象图"],
        ),
        (
            "xstream-deserialization",
            "high",
            "Potential XStream XML deserialization chain",
            "疑似 XStream XML 反序列化链",
            "XStream XML parsing without strict type controls can recover attacker-controlled objects.",
            "XStream XML 解析在缺少严格类型控制时可能恢复攻击者可控对象。",
            re.compile(r"(new\s+XStream\s*\(|\.fromXML\s*\()"),
            ["XML payload", "XStream parser", "Object graph rehydration"],
            ["XML 载荷", "XStream 解析器", "对象图重建"],
        ),
        (
            "expression-injection",
            "high",
            "Potential SpEL expression injection",
            "疑似 SpEL 表达式注入",
            "Dynamic expression parsing can open method invocation or bean access chains.",
            "动态表达式解析可能打开方法调用或 Bean 访问链。",
            re.compile(r"(SpelExpressionParser|parseExpression\s*\()"),
            ["User expression", "Expression parser", "Method or bean invocation"],
            ["用户表达式", "表达式解析器", "方法或 Bean 调用"],
        ),
    ]

    findings: list[VulnerabilityFinding] = []
    for category, severity, title_en, title_zh, summary_en, summary_zh, pattern, chain_en, chain_zh in java_rules:
        for match in pattern.finditer(text):
            line_number = text.count("\n", 0, match.start()) + 1
            evidence = (match.group(0)[:180] + "...") if len(match.group(0)) > 180 else match.group(0)
            findings.append(
                VulnerabilityFinding(
                    id=f"finding-{uuid4().hex[:8]}",
                    title=localize(locale, title_en, title_zh),
                    category=category,
                    severity=severity,  # type: ignore[arg-type]
                    file=relative,
                    line=line_number,
                    summary=localize(locale, summary_en, summary_zh),
                    evidence=evidence,
                    chain=chain_zh if locale == "zh-CN" else chain_en,
                )
            )
    return findings


def build_exploit_chains(
    findings: list[VulnerabilityFinding],
    dependencies: list[DependencyEvidence],
    endpoints: list[EndpointRecord],
    locale: str,
) -> list[ExploitChainCandidate]:
    chains: list[ExploitChainCandidate] = []
    grouped: dict[str, list[VulnerabilityFinding]] = {}
    for finding in findings:
        grouped.setdefault(finding.category, []).append(finding)

    dependency_names = [item.name for item in dependencies]

    for category, related in grouped.items():
        primary = related[0]
        matched_dependencies = [
            name
            for name in dependency_names
            if (
                category == "insecure-deserialization"
                and any(marker in name.lower() for marker in ("jackson", "yaml", "pickle", "fastjson"))
            )
            or (
                category == "auth-bypass"
                and any(marker in name.lower() for marker in ("spring-security", "passport", "casbin", "auth"))
            )
        ][:4]

        chains.append(
            ExploitChainCandidate(
                id=f"chain-{uuid4().hex[:8]}",
                name=localize(locale, f"{primary.title} chain", f"{primary.title} 利用链"),
                category=category,
                confidence="high" if primary.severity in {"critical", "high"} else "medium",
                rationale=localize(
                    locale,
                    f"Finding {primary.id} is reachable from repository sources and has endpoint coverage hints.",
                    f"发现 {primary.id} 可从仓库入口触达，且存在接口覆盖线索。",
                ),
                prerequisites=[
                    localize(locale, "Reach the vulnerable handler", "命中可疑处理函数"),
                    localize(locale, "Preserve payload shape through input validation", "让载荷形态穿过输入校验"),
                ],
                matchedDependencies=matched_dependencies,
                sourceFindings=[item.id for item in related[:3]],
                checks=[
                    ApplicabilityCheck(
                        target=localize(locale, "HTTP ingress", "HTTP 入口"),
                        status="applicable" if endpoints else "uncertain",
                        reason=localize(
                            locale,
                            "Discovered interface routes suggest reachable ingress.",
                            "已发现接口路由，说明存在可达入口。",
                        )
                        if endpoints
                        else localize(
                            locale,
                            "No interface route detected; manual reachability confirmation is needed.",
                            "未发现接口路由，需要人工确认可达性。",
                        ),
                    ),
                    ApplicabilityCheck(
                        target=localize(locale, "Runtime dependency match", "运行时依赖匹配"),
                        status="applicable" if matched_dependencies else "uncertain",
                        reason=localize(
                            locale,
                            "Supporting dependency evidence was found in manifest files.",
                            "在依赖清单中找到了支撑证据。",
                        )
                        if matched_dependencies
                        else localize(
                            locale,
                            "No direct dependency marker was found; rely on code evidence only.",
                            "未找到直接依赖标记，只能依赖代码证据。",
                        ),
                    ),
                ],
                nextStep=localize(
                    locale,
                    "Replay the request path and capture sink arguments at runtime.",
                    "回放请求路径，并在运行时捕获危险调用参数。",
                ),
            )
        )

    return chains[:8]


def build_false_positive_controls(
    findings: list[VulnerabilityFinding],
    endpoints: list[EndpointRecord],
    locale: str,
) -> list[FalsePositiveControl]:
    controls: list[FalsePositiveControl] = []

    controls.append(
        FalsePositiveControl(
            rule=localize(locale, "Only promote findings with concrete code evidence", "仅提升具备明确代码证据的发现"),
            verdict="kept" if findings else "demoted",
            detail=localize(
                locale,
                "Pattern matches were kept only when a concrete sink or guard exception was present.",
                "只有在存在明确危险点或鉴权例外时才保留规则命中。",
            ),
        )
    )

    if any(item.category == "auth-bypass" for item in findings):
        controls.append(
            FalsePositiveControl(
                rule=localize(locale, "Auth bypass requires reachable ingress", "认证绕过必须具备可达入口"),
                verdict="kept" if endpoints else "blocked",
                detail=localize(
                    locale,
                    "Endpoint evidence supports ingress reachability." if endpoints else "No endpoint evidence was found for the auth bypass branch.",
                    "接口证据支持入口可达。" if endpoints else "认证绕过分支暂未找到接口可达证据。",
                ),
            )
        )

    return controls[:6]


def build_exploit_chains_v2(
    findings: list[VulnerabilityFinding],
    dependencies: list[DependencyEvidence],
    environment: EnvironmentFingerprint,
    endpoints: list[EndpointRecord],
    locale: str,
) -> list[ExploitChainCandidate]:
    grouped: dict[str, list[VulnerabilityFinding]] = {}
    for finding in findings:
        grouped.setdefault(finding.category, []).append(finding)

    has_http_ingress = bool(endpoints)
    java_modern = environment.javaVersionHint in {"17", "21"}

    def matched_dependencies(*markers: str) -> list[str]:
        unique: list[str] = []
        for item in dependencies:
            lowered = item.name.lower()
            if any(marker in lowered for marker in markers) and item.name not in unique:
                unique.append(item.name)
        return unique[:6]

    def checks(category: str, deps: list[str], runtime_reason: str, runtime_status: str = "uncertain") -> list[ApplicabilityCheck]:
        return [
            ApplicabilityCheck(
                target=localize(locale, "Ingress reachability", "入口可达性"),
                status="applicable" if has_http_ingress else "uncertain",
                reason=localize(
                    locale,
                    "Discovered routes suggest attacker-reachable ingress." if has_http_ingress else "No route was discovered; manual reachability confirmation is still required.",
                    "发现了接口路由，说明可能存在攻击者可达入口。" if has_http_ingress else "尚未发现接口路由，仍需人工确认可达性。",
                ),
            ),
            ApplicabilityCheck(
                target=localize(locale, "Dependency evidence", "依赖证据"),
                status="applicable" if deps else "blocked",
                reason=localize(
                    locale,
                    f"Matched supporting dependencies: {', '.join(deps)}." if deps else "No supporting dependency marker was found in manifests.",
                    f"匹配到支撑依赖：{', '.join(deps)}。" if deps else "在构建清单中未发现支撑依赖标记。",
                ),
            ),
            ApplicabilityCheck(
                target=localize(locale, "Code sink evidence", "代码落点证据"),
                status="applicable" if grouped.get(category) else "uncertain",
                reason=localize(
                    locale,
                    "Direct code markers were found for this chain." if grouped.get(category) else "This chain is dependency-led and still needs code-level confirmation.",
                    "已发现该链条的直接代码标记。" if grouped.get(category) else "该链条当前主要由依赖驱动，仍需代码级确认。",
                ),
            ),
            ApplicabilityCheck(
                target=localize(locale, "Runtime constraints", "运行时约束"),
                status=runtime_status,  # type: ignore[arg-type]
                reason=runtime_reason,
            ),
        ]

    chains: list[ExploitChainCandidate] = []
    java_specs = [
        (
            "jndi-injection",
            localize(locale, "JNDI remote naming chain", "JNDI 远程命名链"),
            "jndi",
            matched_dependencies("spring-context", "spring-beans", "log4j", "tomcat", "dubbo"),
            localize(
                locale,
                "Modern JDK builds may block several historical remote-class-loading paths." if java_modern else "Exact JDK hardening level is not yet confirmed.",
                "较新的 JDK 版本可能阻断部分历史远程类加载路径。" if java_modern else "尚未确认 JDK 加固级别。",
            ),
            "blocked" if java_modern else "uncertain",
        ),
        (
            "fastjson-autotype",
            localize(locale, "Fastjson AutoType gadget chain", "Fastjson AutoType Gadget 链"),
            "fastjson",
            matched_dependencies("fastjson"),
            localize(
                locale,
                "Dependency or code markers indicate Fastjson parsing behavior that should be validated for AutoType exposure.",
                "依赖或代码标记显示存在 Fastjson 解析行为，需要验证是否暴露 AutoType。",
            ),
            "uncertain",
        ),
        (
            "hessian-deserialization",
            localize(locale, "Hessian or Dubbo deserialization chain", "Hessian 或 Dubbo 反序列化链"),
            "hessian",
            matched_dependencies("hessian", "dubbo"),
            localize(
                locale,
                "This chain is most credible when Hessian or Dubbo manifests are present together with decode paths.",
                "当 Hessian 或 Dubbo 清单与解码路径同时存在时，该链条可信度最高。",
            ),
            "uncertain",
        ),
        (
            "xstream-deserialization",
            localize(locale, "XStream XML deserialization chain", "XStream XML 反序列化链"),
            "xstream",
            matched_dependencies("xstream"),
            localize(
                locale,
                "XStream is highly sensitive to allowlist configuration and explicit type restrictions.",
                "XStream 对白名单配置和显式类型限制极其敏感。",
            ),
            "uncertain",
        ),
        (
            "insecure-deserialization",
            localize(locale, "Java gadget deserialization chain", "Java Gadget 反序列化链"),
            "deserialization",
            matched_dependencies("commons-collections", "jackson-databind", "snakeyaml", "kryo", "fastjson"),
            localize(
                locale,
                "Generic gadget reachability remains plausible when risky serializers and gadget-heavy libraries coexist.",
                "当危险序列化器与 Gadget 密集型依赖并存时，通用 Gadget 可达性仍然成立。",
            ),
            "uncertain",
        ),
        (
            "expression-injection",
            localize(locale, "Spring expression injection chain", "Spring 表达式注入链"),
            "expression",
            matched_dependencies("spring-expression", "spring-core"),
            localize(
                locale,
                "Expression evaluation is especially risky when user data can influence parser input or bean resolution.",
                "当用户数据能够影响表达式解析输入或 Bean 解析时，表达式求值风险会显著上升。",
            ),
            "uncertain",
        ),
    ]

    for category, name, chain_category, deps, runtime_reason, runtime_status in java_specs:
        related = grouped.get(category)
        if not related and not deps:
            continue
        chains.append(
            ExploitChainCandidate(
                id=f"chain-{uuid4().hex[:8]}",
                name=name,
                category=chain_category,
                confidence="high" if related and deps else "medium" if related or deps else "low",
                rationale=localize(
                    locale,
                    f"Java-focused correlation matched {len(related or [])} code indicators and {len(deps)} dependency signals for this chain.",
                    f"面向 Java 的关联分析为该链条匹配到 {len(related or [])} 个代码指示器和 {len(deps)} 个依赖信号。",
                ),
                prerequisites=[
                    localize(locale, "Reach attacker-controlled input", "命中攻击者可控输入"),
                    localize(locale, "Preserve object or expression shape into the sink", "将对象或表达式形态保持到危险落点"),
                ],
                matchedDependencies=deps,
                sourceFindings=[item.id for item in (related or [])[:4]],
                checks=checks(category, deps, runtime_reason, runtime_status),
                nextStep=localize(
                    locale,
                    "Replay the suspected path in an isolated runtime and capture the exact sink arguments before exploit promotion.",
                    "在隔离运行时回放可疑路径，并在提升为可利用前捕获精确落点参数。",
                ),
            )
        )

    generic_specs = [
        ("command-execution", "Command execution replay chain", "command-execution", matched_dependencies("commons-exec")),
        ("auth-bypass", "Framework guard bypass chain", "auth-bypass", matched_dependencies("spring-security", "shiro", "sa-token", "casbin")),
        ("weak-crypto", "Weak cryptography downgrade chain", "weak-crypto", matched_dependencies("bcprov", "shiro")),
    ]
    for category, name_en, chain_category, deps in generic_specs:
        related = grouped.get(category)
        if not related:
            continue
        primary = related[0]
        chains.append(
            ExploitChainCandidate(
                id=f"chain-{uuid4().hex[:8]}",
                name=localize(locale, name_en, name_en),
                category=chain_category,
                confidence="high" if primary.severity in {"critical", "high"} else "medium",
                rationale=localize(
                    locale,
                    f"Finding {primary.id} is backed by concrete sink evidence and {len(deps)} dependency hints.",
                    f"发现 {primary.id} 具备明确落点证据，并伴随 {len(deps)} 个依赖提示。",
                ),
                prerequisites=[
                    localize(locale, "Reach the vulnerable handler", "命中可疑处理函数"),
                    localize(locale, "Preserve payload semantics", "保持载荷语义不被提前消解"),
                ],
                matchedDependencies=deps,
                sourceFindings=[item.id for item in related[:3]],
                checks=checks(
                    category,
                    deps,
                    localize(
                        locale,
                        "Runtime confirmation is still required before raising final exploit confidence.",
                        "在提升最终利用置信度前仍需要运行时确认。",
                    ),
                ),
                nextStep=localize(
                    locale,
                    "Replay the request path and capture sink arguments at runtime.",
                    "回放请求路径，并在运行时捕获危险调用参数。",
                ),
            )
        )

    return chains[:10]


def build_false_positive_controls_v2(
    findings: list[VulnerabilityFinding],
    dependencies: list[DependencyEvidence],
    environment: EnvironmentFingerprint,
    endpoints: list[EndpointRecord],
    locale: str,
) -> list[FalsePositiveControl]:
    controls = build_false_positive_controls(findings, endpoints, locale)

    if any(item.category == "jndi-injection" for item in findings) and environment.javaVersionHint in {"17", "21"}:
        controls.append(
            FalsePositiveControl(
                rule=localize(locale, "Modern JDK remote-loading constraint", "现代 JDK 远程加载约束"),
                verdict="demoted",
                detail=localize(
                    locale,
                    "JDK 17+ reduces several historical JNDI remote-loading paths. Keep only lookup flows with explicit sink evidence.",
                    "JDK 17+ 会收缩部分历史 JNDI 远程加载路径，仅保留具备显式落点证据的查询流。",
                ),
            )
        )

    if any(item.category in {"fastjson-autotype", "hessian-deserialization", "xstream-deserialization"} for item in findings):
        risky_deps = [
            item.name
            for item in dependencies
            if any(marker in item.name.lower() for marker in ("fastjson", "hessian", "dubbo", "xstream"))
        ]
        controls.append(
            FalsePositiveControl(
                rule=localize(locale, "Java chain dependency applicability", "Java 链条依赖适用性"),
                verdict="kept" if risky_deps else "blocked",
                detail=localize(
                    locale,
                    f"Matched dependency evidence: {', '.join(risky_deps[:5])}." if risky_deps else "No supporting Java chain dependency was found; chain promotion is blocked until manifest evidence appears.",
                    f"匹配到的依赖证据：{', '.join(risky_deps[:5])}。" if risky_deps else "未发现支撑该 Java 链条的依赖证据，在出现清单证据前阻断提升。",
                ),
            )
        )

    return controls[:8]


def build_interface_tests(
    endpoints: list[EndpointRecord],
    findings: list[VulnerabilityFinding],
    locale: str,
) -> list[InterfaceTestPlan]:
    category_summary = ", ".join(sorted({item.category for item in findings[:3]})) or localize(locale, "surface mapping", "????")
    return [
        InterfaceTestPlan(
            method=endpoint.method,
            path=endpoint.path,
            objective=localize(
                locale,
                f"Exercise {endpoint.handler} and verify {category_summary} behavior.",
                f"?? {endpoint.handler} ??? {category_summary} ?????",
            ),
            payloadHint=localize(
                locale,
                "Start with authenticated baseline traffic, then mutate risky parameters one field at a time.",
                "???????????????????",
            ),
        )
        for endpoint in endpoints[:12]
    ]


def build_interface_tests_v2(
    endpoints: list[EndpointRecord],
    findings: list[VulnerabilityFinding],
    locale: str,
) -> list[InterfaceTestPlan]:
    category_summary = ", ".join(sorted({item.category for item in findings[:3]})) or localize(locale, "surface mapping", "????")
    plans: list[InterfaceTestPlan] = []
    for endpoint in endpoints[:16]:
        payload_hint = localize(
            locale,
            "Start with authenticated baseline traffic, then mutate risky parameters one field at a time.",
            "???????????????????????",
        )
        if endpoint.method in {"POST", "PUT", "PATCH"}:
            payload_hint = '{"probe":"canglong","mode":"baseline"}'
        elif endpoint.method == "GET" and "?" not in endpoint.path:
            payload_hint = "query: probe=canglong"

        plans.append(
            InterfaceTestPlan(
                method=endpoint.method,
                path=endpoint.path,
                objective=localize(
                    locale,
                    f"Exercise {endpoint.handler} and verify {category_summary} behavior.",
                    f"?? {endpoint.handler} ??? {category_summary} ?????",
                ),
                payloadHint=payload_hint,
            )
        )
    return plans


def _http_probe(url: str) -> tuple[str, list[str], bool, str | None]:
    logs: list[str] = []
    requires_login = False
    login_hint: str | None = None

    try:
        request = Request(url, headers={"User-Agent": "canglong-audit/0.1"})
        with urlopen(request, timeout=2.5) as response:
            logs.append(f"Reachability probe succeeded with HTTP {response.status}: {url}")
            return "completed", logs, requires_login, login_hint
    except HTTPError as exc:
        logs.append(f"Reachability probe returned HTTP {exc.code}: {url}")
        if exc.code in {401, 403}:
            requires_login = True
            login_hint = "Runtime is reachable but requires authentication."
            return "completed", logs, requires_login, login_hint
    except URLError as exc:
        logs.append(f"Runtime probe failed: {exc.reason}")
    except Exception as exc:  # pragma: no cover
        logs.append(f"Runtime probe failed: {format_exception_message(exc)}")

    return "planned", logs, requires_login, login_hint


def build_docker_verification(root: Path, repo_default_base_url: str | None, locale: str) -> DockerVerification:
    dockerfile = next((path for path in root.rglob("Dockerfile") if ".git" not in path.parts), None)
    compose = next(
        (
            path
            for path in root.rglob("*")
            if path.is_file() and path.name in {"docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"}
        ),
        None,
    )

    if not dockerfile and not compose and not repo_default_base_url:
        return DockerVerification(
            status="skipped",
            strategy=localize(
                locale,
                "No Docker assets or runtime target were found for automated verification.",
                "未找到 Docker 资源或运行时目标，自动验证已跳过。",
            ),
        )

    commands: list[str] = []
    if compose:
        commands.append(f"docker compose -f {compose} up -d --build")
    elif dockerfile:
        commands.append(f"docker build -t canglong-audit-target -f {dockerfile} {dockerfile.parent}")

    status_value = "planned"
    logs: list[str] = []
    requires_login = False
    login_hint: str | None = None
    if repo_default_base_url:
        status_value, logs, requires_login, login_hint = _http_probe(repo_default_base_url)
        commands.append(f"curl -i {repo_default_base_url}")

    image_tag = f"canglong/{root.name}:latest" if dockerfile else None
    container_name = f"canglong-{root.name}" if compose or dockerfile else None

    return DockerVerification(
        status=status_value,  # type: ignore[arg-type]
        strategy=localize(
            locale,
            "Use repository Docker assets or the configured runtime URL to validate exploitability.",
            "使用仓库 Docker 资源或配置的运行时地址验证可利用性。",
        ),
        dockerfile=str(dockerfile) if dockerfile else None,
        composeFile=str(compose) if compose else None,
        imageTag=image_tag,
        containerName=container_name,
        commands=commands,
        logs=logs,
        requiresLogin=requires_login,
        loginHint=login_hint,
    )


def _run_command(command: list[str], cwd: Path, timeout: int = 300) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )


def _render_command_logs(command: list[str], result: subprocess.CompletedProcess[str]) -> list[str]:
    lines = [f"$ {' '.join(command)}", f"exit={result.returncode}"]
    if result.stdout:
        lines.extend(line for line in result.stdout.strip().splitlines()[:20] if line)
    if result.stderr:
        lines.extend(line for line in result.stderr.strip().splitlines()[:20] if line)
    return lines


def _extract_container_port(dockerfile: Path) -> int | None:
    text = read_text(dockerfile)
    match = re.search(r"EXPOSE\s+(\d+)", text)
    return int(match.group(1)) if match else None


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _infer_compose_base_url(compose_file: Path) -> str | None:
    text = read_text(compose_file)
    match = re.search(r"['\"]?(\d+):(\d+)['\"]?", text)
    if not match:
        return None
    return f"http://127.0.0.1:{match.group(1)}"


def _looks_like_login(body: str) -> bool:
    lowered = body.lower()
    return any(token in lowered for token in ("login", "sign in", "password", "unauthorized", "bearer"))


def _probe_runtime(base_url: str, endpoints: list[EndpointRecord]) -> tuple[str, list[str], bool, str | None]:
    logs: list[str] = []
    requires_login = False
    login_hint: str | None = None

    probe_paths: list[str] = ["/"]
    for endpoint in endpoints:
        if endpoint.method == "GET" and endpoint.path not in probe_paths:
            probe_paths.append(endpoint.path if endpoint.path.startswith("/") else f"/{endpoint.path}")
        if len(probe_paths) >= 4:
            break

    status = "planned"
    for path in probe_paths:
        url = f"{base_url.rstrip('/')}{path}"
        try:
            request = Request(url, headers={"User-Agent": "canglong-audit/0.1"})
            with urlopen(request, timeout=4) as response:
                body = response.read(400).decode("utf-8", errors="ignore")
                logs.append(f"GET {url} -> {response.status}")
                status = "completed"
                if _looks_like_login(body):
                    requires_login = True
                    login_hint = f"Runtime is reachable, but {path} looks like a login wall."
                    break
        except HTTPError as exc:
            logs.append(f"GET {url} -> {exc.code}")
            if exc.code in {401, 403}:
                requires_login = True
                login_hint = f"Runtime is reachable, but {path} returned HTTP {exc.code} without credentials."
                return "completed", logs, requires_login, login_hint
        except URLError as exc:
            logs.append(f"GET {url} -> probe failed: {exc.reason}")
            return status, logs, requires_login, login_hint
        except Exception as exc:  # pragma: no cover
            logs.append(f"GET {url} -> probe failed: {format_exception_message(exc)}")
            return status, logs, requires_login, login_hint

    return status, logs, requires_login, login_hint


def build_docker_verification_v2(
    root: Path,
    repo_default_base_url: str | None,
    endpoints: list[EndpointRecord],
    locale: str,
) -> DockerVerification:
    dockerfile = next((path for path in root.rglob("Dockerfile") if ".git" not in path.parts), None)
    compose = next(
        (
            path
            for path in root.rglob("*")
            if path.is_file() and path.name in {"docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"}
        ),
        None,
    )

    verification = DockerVerification(
        status="planned",
        strategy=localize(
            locale,
            "Prefer real Docker deployment when assets are available, then probe the runtime and record whether manual login is required.",
            "优先在存在 Docker 资产时真实部署，再探测运行时并记录是否需要人工登录。",
        ),
    )

    verification.dockerfile = str(dockerfile) if dockerfile else None
    verification.composeFile = str(compose) if compose else None

    version_result = _run_command(["docker", "--version"], root, timeout=20)
    verification.logs.extend(_render_command_logs(["docker", "--version"], version_result))
    if version_result.returncode != 0:
        verification.status = "failed"
        return verification

    if not dockerfile and not compose and not repo_default_base_url:
        verification.status = "skipped"
        verification.strategy = localize(
            locale,
            "No Dockerfile, Compose manifest, or runtime base URL was found for automated verification.",
            "未发现 Dockerfile、Compose 清单或运行时基础 URL，已跳过自动验证。",
        )
        return verification

    if compose:
        up_command = ["docker", "compose", "-f", str(compose), "up", "-d", "--build"]
        verification.commands.append(" ".join(up_command))
        up_result = _run_command(up_command, root, timeout=900)
        verification.logs.extend(_render_command_logs(up_command, up_result))
        if up_result.returncode != 0:
            verification.status = "failed"
            return verification

        ps_command = ["docker", "compose", "-f", str(compose), "ps"]
        ps_result = _run_command(ps_command, root, timeout=60)
        verification.logs.extend(_render_command_logs(ps_command, ps_result))

        base_url = repo_default_base_url or _infer_compose_base_url(compose)
        if base_url:
            status_value, logs, requires_login, login_hint = _probe_runtime(base_url, endpoints)
            verification.logs.extend(logs)
            verification.requiresLogin = requires_login
            verification.loginHint = login_hint
            verification.status = "completed" if status_value == "completed" else "running"
        else:
            verification.status = "completed"

        down_command = ["docker", "compose", "-f", str(compose), "down"]
        verification.commands.append(" ".join(down_command))
        down_result = _run_command(down_command, root, timeout=300)
        verification.logs.extend(_render_command_logs(down_command, down_result))
        return verification

    if dockerfile:
        image_tag = f"canglong-{root.name.lower()}-{uuid4().hex[:6]}"
        container_name = f"canglong-{root.name.lower()}-{uuid4().hex[:6]}"
        verification.imageTag = image_tag
        verification.containerName = container_name

        build_command = ["docker", "build", "-t", image_tag, "-f", str(dockerfile), str(dockerfile.parent)]
        verification.commands.append(" ".join(build_command))
        build_result = _run_command(build_command, root, timeout=1200)
        verification.logs.extend(_render_command_logs(build_command, build_result))
        if build_result.returncode != 0:
            verification.status = "failed"
            return verification

        container_port = _extract_container_port(dockerfile) or 8000
        host_port = _find_free_port()
        run_command = ["docker", "run", "-d", "--name", container_name, "-p", f"{host_port}:{container_port}", image_tag]
        verification.commands.append(" ".join(run_command))
        run_result = _run_command(run_command, root, timeout=120)
        verification.logs.extend(_render_command_logs(run_command, run_result))
        if run_result.returncode != 0:
            verification.status = "failed"
            return verification

        time.sleep(6)
        logs_command = ["docker", "logs", "--tail", "60", container_name]
        container_logs = _run_command(logs_command, root, timeout=60)
        verification.logs.extend(_render_command_logs(logs_command, container_logs))

        base_url = repo_default_base_url or f"http://127.0.0.1:{host_port}"
        status_value, logs, requires_login, login_hint = _probe_runtime(base_url, endpoints)
        verification.logs.extend(logs)
        verification.requiresLogin = requires_login
        verification.loginHint = login_hint
        verification.status = "completed" if status_value == "completed" else "running"

        cleanup_command = ["docker", "rm", "-f", container_name]
        verification.commands.append(" ".join(cleanup_command))
        cleanup_result = _run_command(cleanup_command, root, timeout=60)
        verification.logs.extend(_render_command_logs(cleanup_command, cleanup_result))
        return verification

    status_value, logs, requires_login, login_hint = _probe_runtime(repo_default_base_url or "http://127.0.0.1", endpoints)
    verification.logs.extend(logs)
    verification.requiresLogin = requires_login
    verification.loginHint = login_hint
    verification.status = "completed" if status_value == "completed" else "planned"
    return verification


def _normalize_probe_path(path: str) -> str:
    if not path:
        return "/"
    normalized = path.strip() or "/"
    normalized = re.sub(r"\{[^/]+\}", "canglong", normalized)
    normalized = re.sub(r":[A-Za-z_][A-Za-z0-9_]*", "canglong", normalized)
    normalized = re.sub(r"/{2,}", "/", normalized)
    return normalized if normalized.startswith("/") else f"/{normalized}"


def _probe_runtime_v2(
    base_url: str,
    interface_tests: list[InterfaceTestPlan],
    endpoints: list[EndpointRecord],
) -> tuple[str, list[str], bool, str | None]:
    logs: list[str] = []
    requires_login = False
    login_hint: str | None = None
    status = "planned"

    selected_tests: list[InterfaceTestPlan] = []
    selected_tests.extend(
        item
        for item in interface_tests
        if item.method == "GET" and _normalize_probe_path(item.path) in {"/", "/health", "/healthz", "/status"}
    )
    selected_tests.extend(item for item in interface_tests if item.method in {"POST", "PUT", "PATCH"})
    selected_tests.extend(item for item in interface_tests if item.method == "GET")
    deduped: list[InterfaceTestPlan] = []
    seen: set[tuple[str, str]] = set()
    for test in selected_tests:
        key = (test.method, test.path)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(test)
        if len(deduped) >= 6:
            break

    if not deduped:
        deduped = [
            InterfaceTestPlan(method="GET", path="/", objective="Root reachability", payloadHint="query: probe=canglong")
        ]
        for endpoint in endpoints:
            if endpoint.method == "GET":
                deduped.append(
                    InterfaceTestPlan(
                        method="GET",
                        path=endpoint.path,
                        objective=f"Reach {endpoint.handler}",
                        payloadHint="query: probe=canglong",
                    )
                )
            if len(deduped) >= 4:
                break

    for test in deduped:
        if test.method == "DELETE":
            logs.append(f"SKIP {test.method} {test.path} -> destructive method skipped")
            continue

        path = _normalize_probe_path(test.path)
        url = f"{base_url.rstrip('/')}{path}"
        headers = {"User-Agent": "canglong-audit/0.1"}
        data: bytes | None = None
        method = test.method

        if method in {"POST", "PUT", "PATCH"}:
            headers["Content-Type"] = "application/json"
            data = test.payloadHint.encode("utf-8")
        elif method == "GET" and test.payloadHint.startswith("query:") and "?" not in url:
            url = f"{url}?probe=canglong"

        try:
            request = Request(url, headers=headers, data=data, method=method)
            with urlopen(request, timeout=5) as response:
                body = response.read(400).decode("utf-8", errors="ignore")
                logs.append(f"{method} {url} -> {response.status}")
                status = "completed"
                if _looks_like_login(body):
                    requires_login = True
                    login_hint = f"Runtime is reachable, but {path} looks like a login wall."
                    break
        except HTTPError as exc:
            logs.append(f"{method} {url} -> {exc.code}")
            if exc.code in {401, 403}:
                requires_login = True
                login_hint = f"Runtime is reachable, but {path} returned HTTP {exc.code} without credentials."
                return "completed", logs, requires_login, login_hint
            if exc.code in {400, 404, 405, 415, 422}:
                status = "completed"
        except URLError as exc:
            logs.append(f"{method} {url} -> probe failed: {exc.reason}")
            return status, logs, requires_login, login_hint
        except Exception as exc:  # pragma: no cover
            logs.append(f"{method} {url} -> probe failed: {format_exception_message(exc)}")
            return status, logs, requires_login, login_hint

    return status, logs, requires_login, login_hint


def build_docker_verification_v3(
    root: Path,
    repo_default_base_url: str | None,
    endpoints: list[EndpointRecord],
    interface_tests: list[InterfaceTestPlan],
    locale: str,
) -> DockerVerification:
    dockerfile = next((path for path in root.rglob("Dockerfile") if ".git" not in path.parts), None)
    compose = next(
        (
            path
            for path in root.rglob("*")
            if path.is_file() and path.name in {"docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"}
        ),
        None,
    )

    verification = DockerVerification(
        status="planned",
        strategy=localize(
            locale,
            "Prefer real Docker deployment when assets are available, then replay interface probes before teardown and record whether manual login is required.",
            "优先使用真实 Docker 部署，在清理前完成接口回放探测，并记录是否需要人工登录。",
        ),
        dockerfile=str(dockerfile) if dockerfile else None,
        composeFile=str(compose) if compose else None,
    )

    version_result = _run_command(["docker", "--version"], root, timeout=20)
    verification.logs.extend(_render_command_logs(["docker", "--version"], version_result))
    if version_result.returncode != 0:
        verification.status = "failed"
        return verification

    if not dockerfile and not compose and not repo_default_base_url:
        verification.status = "skipped"
        verification.strategy = localize(
            locale,
            "No Dockerfile, Compose manifest, or runtime base URL was found for automated verification.",
            "未发现 Dockerfile、Compose 清单或运行时基础 URL，已跳过自动验证。",
        )
        return verification

    if compose:
        up_command = ["docker", "compose", "-f", str(compose), "up", "-d", "--build"]
        down_command = ["docker", "compose", "-f", str(compose), "down"]
        verification.commands.extend([" ".join(up_command), " ".join(down_command)])
        compose_started = False
        try:
            up_result = _run_command(up_command, root, timeout=900)
            verification.logs.extend(_render_command_logs(up_command, up_result))
            if up_result.returncode != 0:
                verification.status = "failed"
                return verification

            compose_started = True
            time.sleep(6)

            ps_command = ["docker", "compose", "-f", str(compose), "ps"]
            ps_result = _run_command(ps_command, root, timeout=60)
            verification.logs.extend(_render_command_logs(ps_command, ps_result))

            base_url = repo_default_base_url or _infer_compose_base_url(compose)
            if base_url:
                status_value, logs, requires_login, login_hint = _probe_runtime_v2(base_url, interface_tests, endpoints)
                verification.logs.extend(logs)
                verification.requiresLogin = requires_login
                verification.loginHint = login_hint
                verification.status = "completed" if status_value == "completed" else "running"
            else:
                verification.status = "completed"
            return verification
        finally:
            if compose_started:
                down_result = _run_command(down_command, root, timeout=300)
                verification.logs.extend(_render_command_logs(down_command, down_result))

    if dockerfile:
        image_tag = f"canglong-{root.name.lower()}-{uuid4().hex[:6]}"
        container_name = f"canglong-{root.name.lower()}-{uuid4().hex[:6]}"
        verification.imageTag = image_tag
        verification.containerName = container_name

        build_command = ["docker", "build", "-t", image_tag, "-f", str(dockerfile), str(dockerfile.parent)]
        run_port = _extract_container_port(dockerfile) or 8000
        host_port = _find_free_port()
        run_command = ["docker", "run", "-d", "--name", container_name, "-p", f"{host_port}:{run_port}", image_tag]
        cleanup_command = ["docker", "rm", "-f", container_name]
        verification.commands.extend([" ".join(build_command), " ".join(run_command), " ".join(cleanup_command)])

        container_started = False
        try:
            build_result = _run_command(build_command, root, timeout=1200)
            verification.logs.extend(_render_command_logs(build_command, build_result))
            if build_result.returncode != 0:
                verification.status = "failed"
                return verification

            run_result = _run_command(run_command, root, timeout=120)
            verification.logs.extend(_render_command_logs(run_command, run_result))
            if run_result.returncode != 0:
                verification.status = "failed"
                return verification

            container_started = True
            time.sleep(6)

            logs_command = ["docker", "logs", "--tail", "60", container_name]
            container_logs = _run_command(logs_command, root, timeout=60)
            verification.logs.extend(_render_command_logs(logs_command, container_logs))

            base_url = repo_default_base_url or f"http://127.0.0.1:{host_port}"
            status_value, logs, requires_login, login_hint = _probe_runtime_v2(base_url, interface_tests, endpoints)
            verification.logs.extend(logs)
            verification.requiresLogin = requires_login
            verification.loginHint = login_hint
            verification.status = "completed" if status_value == "completed" else "running"
            return verification
        finally:
            if container_started:
                cleanup_result = _run_command(cleanup_command, root, timeout=60)
                verification.logs.extend(_render_command_logs(cleanup_command, cleanup_result))

    status_value, logs, requires_login, login_hint = _probe_runtime_v2(repo_default_base_url or "http://127.0.0.1", interface_tests, endpoints)
    verification.logs.extend(logs)
    verification.requiresLogin = requires_login
    verification.loginHint = login_hint
    verification.status = "completed" if status_value == "completed" else "planned"
    return verification


def build_recommendations(
    findings: list[VulnerabilityFinding],
    docker_verification: DockerVerification,
    locale: str,
) -> list[str]:
    recommendations: list[str] = []
    categories = {item.category for item in findings}

    if "command-execution" in categories:
        recommendations.append(
            localize(
                locale,
                "Remove shell=True or equivalent command concatenation paths, and bind arguments explicitly.",
                "移除 shell=True 或同类命令拼接路径，改为显式参数绑定。",
            )
        )
    if "insecure-deserialization" in categories:
        recommendations.append(
            localize(
                locale,
                "Replace unsafe deserializers with allowlisted object mapping or schema-validated codecs.",
                "将不安全反序列化替换为白名单对象映射或带 schema 校验的编解码器。",
            )
        )
    if {"jndi-injection", "fastjson-autotype", "hessian-deserialization", "xstream-deserialization"} & categories:
        recommendations.append(
            localize(
                locale,
                "Pin Java library versions, disable risky type-resolution features, and verify applicability against the exact runtime before escalating any exploit chain.",
                "固定 Java 依赖版本，关闭危险类型解析能力，并在提升任何利用链前结合真实运行时确认其适用性。",
            )
        )
    if "auth-bypass" in categories:
        recommendations.append(
            localize(
                locale,
                "Re-check guard ordering and deny-by-default behavior on public routes.",
                "重新核查守卫顺序，并确保公开路由遵循默认拒绝策略。",
            )
        )
    if docker_verification.status == "failed":
        recommendations.append(
            localize(
                locale,
                "Docker verification failed. Fix the build or startup path before treating static findings as runtime-confirmed.",
                "Docker 验证失败。在把静态发现视为运行时已确认之前，应先修复构建或启动链路。",
            )
        )
    if docker_verification.requiresLogin and docker_verification.loginHint:
        recommendations.append(docker_verification.loginHint)
    if docker_verification.status in {"planned", "skipped"}:
        recommendations.append(
            localize(
                locale,
                "Stage a runnable verification target so high-signal findings can be replayed before promotion.",
                "准备可运行的验证目标，让高信号发现能在升级前完成回放验证。",
            )
        )
    if not recommendations:
        recommendations.append(
            localize(
                locale,
                "Continue expanding endpoint coverage and dependency evidence before raising severity.",
                "继续补齐接口覆盖与依赖证据，再提升风险等级。",
            )
        )

    return recommendations[:8]


class AuditService:
    def __init__(self) -> None:
        self._jobs: dict[str, AuditJob] = {}
        self._reports: dict[str, AuditReport] = {}
        self._lock = threading.Lock()

    def list_jobs(self) -> list[AuditJob]:
        with self._lock:
            return sorted(self._jobs.values(), key=lambda item: item.createdAt, reverse=True)

    def get_job(self, job_id: str) -> AuditJob:
        with self._lock:
            job = self._jobs.get(job_id)
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit job not found")
        return job

    def get_report(self, report_id: str) -> AuditReport:
        with self._lock:
            report = self._reports.get(report_id)
        if not report:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit report not found")
        return report

    def start_job(self, repo_id: str, lang: str = "en") -> AuditJob:
        locale = normalize_locale(lang)
        repo = repo_store.get_repo(repo_id)

        if repo.sourceType == "git" and not Path(repo.localPath).exists():
            sync_repo(repo)

        if repo.sourceType == "local":
            local_path = Path(repo.localPath)
            if not local_path.exists() or not local_path.is_dir():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Local source path is unavailable")

        timestamp = utc_now()
        job = AuditJob(
            id=f"audit-{uuid4().hex[:8]}",
            repoId=repo.id,
            repoName=repo.name,
            status="queued",
            progress=0,
            currentStep=localize(locale, "Queued for audit", "等待审计"),
            findings=0,
            endpoints=0,
            createdAt=timestamp,
            updatedAt=timestamp,
            reportId=None,
            verificationStatus="planned",
            stages=self._build_stages(locale),
            error=None,
        )

        with self._lock:
            self._jobs[job.id] = job

        worker = threading.Thread(target=self._run_job, args=(job.id, locale), daemon=True)
        worker.start()
        return job

    def _build_stages(self, locale: str) -> list[AuditStage]:
        return [
            AuditStage(
                name=localize(locale, "Repository readiness", "仓库就绪检查"),
                status="pending",
                detail=localize(locale, "Validate repository source and prepare scan set.", "校验仓库来源并准备扫描集。"),
            ),
            AuditStage(
                name=localize(locale, "Environment fingerprint", "环境指纹识别"),
                status="pending",
                detail=localize(locale, "Detect languages, frameworks, and dependency evidence.", "识别语言、框架与依赖证据。"),
            ),
            AuditStage(
                name=localize(locale, "Endpoint and flow mapping", "接口与业务流梳理"),
                status="pending",
                detail=localize(locale, "Discover interfaces and approximate business call paths.", "发现接口并推断业务调用路径。"),
            ),
            AuditStage(
                name=localize(locale, "Static correlation", "静态关联分析"),
                status="pending",
                detail=localize(locale, "Rank findings, chain candidates, and false-positive controls.", "评估发现、利用链候选和误报抑制项。"),
            ),
            AuditStage(
                name=localize(locale, "Docker verification", "Docker 验证"),
                status="pending",
                detail=localize(locale, "Deploy and replay the code path when a Docker target is available.", "当存在 Docker 目标时进行部署与回放验证。"),
            ),
            AuditStage(
                name=localize(locale, "Report assembly", "报告组装"),
                status="pending",
                detail=localize(locale, "Compile the evidence report for analyst review.", "生成面向分析师的证据报告。"),
            ),
        ]

    def _update_job(self, job_id: str, **changes: object) -> AuditJob:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit job not found")
            for key, value in changes.items():
                setattr(job, key, value)
            job.updatedAt = utc_now()
            return job

    def _update_stage(
        self,
        job_id: str,
        stage_index: int,
        stage_status: str,
        detail: str | None = None,
    ) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit job not found")
            if 0 <= stage_index < len(job.stages):
                stage = job.stages[stage_index]
                stage.status = stage_status  # type: ignore[assignment]
                if detail is not None:
                    stage.detail = detail
                job.updatedAt = utc_now()

    def _complete_stage(self, job_id: str, stage_index: int, progress: int, current_step: str, detail: str | None = None) -> None:
        self._update_stage(job_id, stage_index, "completed", detail)
        self._update_job(job_id, progress=progress, currentStep=current_step)

    def _fail_job(self, job_id: str, stage_index: int | None, locale: str, error: Exception) -> None:
        if stage_index is not None:
            self._update_stage(
                job_id,
                stage_index,
                "failed",
                localize(
                    locale,
                    f"Stage failed: {format_exception_message(error)}",
                    f"阶段失败：{format_exception_message(error)}",
                ),
            )
        self._update_job(
            job_id,
            status="failed",
            currentStep=localize(locale, "Audit failed", "审计失败"),
            error=format_exception_message(error),
        )

    def _run_job(self, job_id: str, locale: str) -> None:
        stage_index: int | None = None
        try:
            job = self.get_job(job_id)
            repo = repo_store.get_repo(job.repoId)
            root = Path(repo.localPath)
            if not root.exists():
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository workspace not found")

            self._update_job(job_id, status="running", progress=3, currentStep=localize(locale, "Preparing repository", "准备仓库"))

            stage_index = 0
            self._update_stage(job_id, stage_index, "running")
            source_files = iter_repository_files(root)
            if not source_files:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="No analyzable files found")
            self._complete_stage(
                job_id,
                stage_index,
                14,
                localize(locale, "Repository ready", "仓库就绪"),
                localize(locale, f"Prepared {len(source_files)} candidate files for audit.", f"已准备 {len(source_files)} 个候选文件用于审计。"),
            )

            stage_index = 1
            self._update_stage(job_id, stage_index, "running")
            environment = build_environment_fingerprint(root, source_files)
            dependencies = collect_dependencies(root, source_files)
            self._complete_stage(
                job_id,
                stage_index,
                32,
                localize(locale, "Environment fingerprinted", "环境指纹完成"),
                localize(
                    locale,
                    f"Detected {len(environment.languages)} language lanes and {len(dependencies)} dependency records.",
                    f"识别出 {len(environment.languages)} 条语言链路和 {len(dependencies)} 条依赖记录。",
                ),
            )

            stage_index = 2
            self._update_stage(job_id, stage_index, "running")
            endpoints = discover_endpoints(root, source_files)
            self._update_job(job_id, endpoints=len(endpoints))
            self._complete_stage(
                job_id,
                stage_index,
                54,
                localize(locale, "Endpoint map prepared", "接口地图完成"),
                localize(locale, f"Discovered {len(endpoints)} interface candidates.", f"发现 {len(endpoints)} 个接口候选。"),
            )

            stage_index = 3
            self._update_stage(job_id, stage_index, "running")
            findings = scan_findings(root, source_files, locale)
            exploit_chains = build_exploit_chains_v2(findings, dependencies, environment, endpoints, locale)
            false_positive_controls = build_false_positive_controls_v2(findings, dependencies, environment, endpoints, locale)
            self._update_job(job_id, findings=len(findings))
            self._complete_stage(
                job_id,
                stage_index,
                74,
                localize(locale, "Static correlation completed", "静态关联完成"),
                localize(
                    locale,
                    f"Promoted {len(findings)} findings and {len(exploit_chains)} exploit-chain candidates.",
                    f"提升了 {len(findings)} 个发现和 {len(exploit_chains)} 个利用链候选。",
                ),
            )

            interface_tests = build_interface_tests_v2(endpoints, findings, locale)

            stage_index = 4
            self._update_stage(job_id, stage_index, "running")
            docker_verification = build_docker_verification_v3(root, repo.defaultBaseUrl, endpoints, interface_tests, locale)
            self._update_job(job_id, verificationStatus=docker_verification.status)
            self._complete_stage(job_id, stage_index, 88, localize(locale, "Verification strategy ready", "验证策略完成"), docker_verification.strategy)

            stage_index = 5
            self._update_stage(job_id, stage_index, "running")
            summary = AuditSummary(
                filesScanned=len(source_files),
                endpointsDiscovered=len(endpoints),
                businessFlowsMapped=max(len(endpoints), min(len(source_files), max(1, len(findings) + len(exploit_chains)))),
                findingsTotal=len(findings),
                criticalFindings=sum(1 for item in findings if item.severity == "critical"),
                highFindings=sum(1 for item in findings if item.severity == "high"),
            )
            report = AuditReport(
                id=f"report-{uuid4().hex[:8]}",
                jobId=job_id,
                repoId=repo.id,
                repoName=repo.name,
                generatedAt=utc_now(),
                summary=summary,
                environment=environment,
                dependencies=dependencies,
                exploitChains=exploit_chains,
                falsePositiveControls=false_positive_controls,
                dockerVerification=docker_verification,
                endpointMap=endpoints,
                interfaceTests=interface_tests,
                findings=findings,
                recommendations=build_recommendations(findings, docker_verification, locale),
            )

            with self._lock:
                self._reports[report.id] = report

            repo.lastAuditAt = utc_now()
            repo.status = "ready"
            repo.summary = localize(
                locale,
                f"Latest audit completed with {len(findings)} findings and {len(endpoints)} endpoints.",
                f"最近一次审计完成，产出 {len(findings)} 个发现和 {len(endpoints)} 个接口。",
            )
            repo_store.update_repo(repo)

            self._update_stage(job_id, stage_index, "completed", localize(locale, "Evidence report generated.", "证据报告已生成。"))
            self._update_job(
                job_id,
                status="completed",
                progress=100,
                currentStep=localize(locale, "Audit complete", "审计完成"),
                reportId=report.id,
                error=None,
            )
        except Exception as exc:  # pragma: no cover
            repo_job = self._jobs.get(job_id)
            if repo_job is not None:
                try:
                    repo = repo_store.get_repo(repo_job.repoId)
                    repo.status = "audit_failed"
                    repo.summary = format_exception_message(exc)
                    repo_store.update_repo(repo)
                except Exception:
                    pass
            self._fail_job(job_id, stage_index, locale, exc)


audit_service = AuditService()
