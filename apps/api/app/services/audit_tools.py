"""
审计工具系统 - 借鉴claw-code的工具架构
提供结构化的审计工具注册、权限控制和执行管理
"""
from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional


class AuditToolPermission(Enum):
    """审计工具权限级别"""
    READ_ONLY = "read_only"
    ANALYSIS = "analysis"
    MODIFICATION = "modification"
    DANGEROUS = "dangerous"


@dataclass(frozen=True)
class AuditToolMetadata:
    """审计工具元数据"""
    name: str
    description: str
    category: str
    permission: AuditToolPermission
    supported_languages: tuple[str, ...] = ()
    requires_context: bool = False


@dataclass
class AuditToolResult:
    """审计工具执行结果"""
    tool_name: str
    success: bool
    findings: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    execution_time: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class AuditTool(ABC):
    """审计工具基类"""
    
    def __init__(self, metadata: AuditToolMetadata):
        self.metadata = metadata
    
    @abstractmethod
    def execute(self, context: dict[str, Any]) -> AuditToolResult:
        """执行审计工具"""
        pass
    
    def can_execute(self, context: dict[str, Any]) -> bool:
        """检查工具是否可以执行"""
        if self.metadata.requires_context and not context:
            return False
        return True


class AuditToolRegistry:
    """审计工具注册表"""
    
    def __init__(self):
        self._tools: dict[str, AuditTool] = {}
        self._permission_filters: dict[AuditToolPermission, Callable[[AuditToolMetadata], bool]] = {}
    
    def register(self, tool: AuditTool) -> None:
        """注册审计工具"""
        self._tools[tool.metadata.name] = tool
    
    def get_tool(self, name: str) -> Optional[AuditTool]:
        """获取审计工具"""
        return self._tools.get(name)
    
    def get_tools_by_permission(self, permission: AuditToolPermission) -> list[AuditTool]:
        """根据权限级别获取工具"""
        return [
            tool for tool in self._tools.values()
            if tool.metadata.permission == permission
        ]
    
    def get_tools_by_language(self, language: str) -> list[AuditTool]:
        """根据编程语言获取工具"""
        return [
            tool for tool in self._tools.values()
            if not tool.metadata.supported_languages or language in tool.metadata.supported_languages
        ]
    
    def get_tools_by_category(self, category: str) -> list[AuditTool]:
        """根据类别获取工具"""
        return [
            tool for tool in self._tools.values()
            if tool.metadata.category == category
        ]
    
    def list_all_tools(self) -> list[AuditToolMetadata]:
        """列出所有工具的元数据"""
        return [tool.metadata for tool in self._tools.values()]


class SecurityPatternTool(AuditTool):
    """安全模式检测工具"""
    
    def __init__(self, pattern: re.Pattern, metadata: AuditToolMetadata):
        super().__init__(metadata)
        self.pattern = pattern
    
    def execute(self, context: dict[str, Any]) -> AuditToolResult:
        """执行安全模式检测"""
        import time
        start_time = time.time()
        
        findings = []
        errors = []
        
        try:
            code_content = context.get('code_content', '')
            file_path = context.get('file_path', '')
            
            if not code_content:
                return AuditToolResult(
                    tool_name=self.metadata.name,
                    success=False,
                    errors=["No code content provided"]
                )
            
            matches = self.pattern.finditer(code_content)
            for match in matches:
                line_number = code_content[:match.start()].count('\n') + 1
                matched_text = match.group()
                
                findings.append({
                    'file_path': file_path,
                    'line_number': line_number,
                    'matched_text': matched_text,
                    'pattern': self.pattern.pattern,
                    'severity': self._get_severity(),
                    'category': self.metadata.category
                })
            
        except Exception as e:
            errors.append(f"Pattern matching error: {str(e)}")
        
        execution_time = time.time() - start_time
        
        return AuditToolResult(
            tool_name=self.metadata.name,
            success=len(errors) == 0,
            findings=findings,
            errors=errors,
            execution_time=execution_time
        )
    
    def _get_severity(self) -> str:
        """根据权限级别确定严重性"""
        severity_map = {
            AuditToolPermission.DANGEROUS: 'critical',
            AuditToolPermission.MODIFICATION: 'high',
            AuditToolPermission.ANALYSIS: 'medium',
            AuditToolPermission.READ_ONLY: 'low'
        }
        return severity_map.get(self.metadata.permission, 'medium')


class DependencyAnalysisTool(AuditTool):
    """依赖分析工具"""
    
    def execute(self, context: dict[str, Any]) -> AuditToolResult:
        """执行依赖分析"""
        import time
        start_time = time.time()
        
        findings = []
        errors = []
        
        try:
            dependencies = context.get('dependencies', {})
            language = context.get('language', '')
            
            if not dependencies:
                return AuditToolResult(
                    tool_name=self.metadata.name,
                    success=False,
                    errors=["No dependencies provided"]
                )
            
            # 分析已知漏洞依赖
            known_vulnerable_deps = self._check_known_vulnerabilities(dependencies, language)
            findings.extend(known_vulnerable_deps)
            
            # 分析过时依赖
            outdated_deps = self._check_outdated_dependencies(dependencies)
            findings.extend(outdated_deps)
            
        except Exception as e:
            errors.append(f"Dependency analysis error: {str(e)}")
        
        execution_time = time.time() - start_time
        
        return AuditToolResult(
            tool_name=self.metadata.name,
            success=len(errors) == 0,
            findings=findings,
            errors=errors,
            execution_time=execution_time
        )
    
    def _check_known_vulnerabilities(self, dependencies: dict, language: str) -> list[dict]:
        """检查已知漏洞依赖"""
        # 这里可以集成CVE数据库或其他漏洞数据库
        vulnerable_deps = []
        
        # 示例：检查一些已知的有漏洞版本
        known_vulnerabilities = {
            'python': {
                'requests': ['<2.20.0'],
                'urllib3': ['<1.24.2'],
            },
            'java': {
                'log4j': ['2.0-beta9', '2.14.1'],
                'jackson-databind': ['2.9.10.8'],
            }
        }
        
        lang_vulns = known_vulnerabilities.get(language, {})
        
        for dep_name, version in dependencies.items():
            if dep_name in lang_vulns:
                vuln_versions = lang_vulns[dep_name]
                if any(self._version_matches(version, v) for v in vuln_versions):
                    vulnerable_deps.append({
                        'dependency': dep_name,
                        'version': version,
                        'vulnerability': 'Known security vulnerability',
                        'severity': 'critical',
                        'category': 'dependency'
                    })
        
        return vulnerable_deps
    
    def _check_outdated_dependencies(self, dependencies: dict) -> list[dict]:
        """检查过时依赖"""
        # 这里可以集成版本检查API
        outdated = []
        
        # 示例：检查一些明显过时的版本
        outdated_thresholds = {
            'requests': '2.25.0',
            'numpy': '1.20.0',
            'django': '3.2.0',
        }
        
        for dep_name, version in dependencies.items():
            if dep_name in outdated_thresholds:
                threshold = outdated_thresholds[dep_name]
                if self._version_compare(version, threshold) < 0:
                    outdated.append({
                        'dependency': dep_name,
                        'current_version': version,
                        'recommended_version': threshold,
                        'vulnerability': 'Outdated dependency',
                        'severity': 'medium',
                        'category': 'dependency'
                    })
        
        return outdated
    
    def _version_matches(self, version: str, pattern: str) -> bool:
        """检查版本是否匹配模式"""
        # 简化的版本匹配逻辑
        if pattern.startswith('<'):
            return self._version_compare(version, pattern[1:]) < 0
        elif pattern.startswith('<='):
            return self._version_compare(version, pattern[2:]) <= 0
        elif pattern.startswith('>'):
            return self._version_compare(version, pattern[1:]) > 0
        elif pattern.startswith('>='):
            return self._version_compare(version, pattern[2:]) >= 0
        return version == pattern
    
    def _version_compare(self, v1: str, v2: str) -> int:
        """比较两个版本号"""
        try:
            v1_parts = [int(x) for x in v1.split('.')]
            v2_parts = [int(x) for x in v2.split('.')]
            
            for a, b in zip(v1_parts, v2_parts):
                if a < b:
                    return -1
                elif a > b:
                    return 1
            
            if len(v1_parts) < len(v2_parts):
                return -1
            elif len(v1_parts) > len(v2_parts):
                return 1
            
            return 0
        except (ValueError, AttributeError):
            return 0


# 创建全局工具注册表
audit_tool_registry = AuditToolRegistry()


def register_default_tools() -> None:
    """注册默认的审计工具"""
    # SQL注入检测工具
    sql_injection_tool = SecurityPatternTool(
        pattern=re.compile(
            r'(execute\s*\(\s*[\'"]\s*\+|query\s*\(\s*[\'"]\s*\+|\.execute\s*\([^)]*\+|\.query\s*\([^)]*\+)',
            re.IGNORECASE
        ),
        metadata=AuditToolMetadata(
            name="sql_injection_detector",
            description="Detects potential SQL injection vulnerabilities",
            category="injection",
            permission=AuditToolPermission.ANALYSIS,
            supported_languages=("python", "java", "javascript", "typescript")
        )
    )
    audit_tool_registry.register(sql_injection_tool)
    
    # 命令注入检测工具
    command_injection_tool = SecurityPatternTool(
        pattern=re.compile(
            r'(subprocess\.run\(.*shell\s*=\s*True|os\.system\(|Runtime\.exec\(|ProcessBuilder\()',
            re.IGNORECASE
        ),
        metadata=AuditToolMetadata(
            name="command_injection_detector",
            description="Detects potential command injection vulnerabilities",
            category="injection",
            permission=AuditToolPermission.DANGEROUS,
            supported_languages=("python", "java")
        )
    )
    audit_tool_registry.register(command_injection_tool)
    
    # 依赖分析工具
    dependency_tool = DependencyAnalysisTool(
        metadata=AuditToolMetadata(
            name="dependency_analyzer",
            description="Analyzes dependencies for known vulnerabilities and outdated packages",
            category="dependency",
            permission=AuditToolPermission.READ_ONLY,
            requires_context=True
        )
    )
    audit_tool_registry.register(dependency_tool)


# 初始化默认工具
register_default_tools()
