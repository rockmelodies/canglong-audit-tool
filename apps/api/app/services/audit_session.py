"""
审计会话管理 - 借鉴claw-code的会话管理架构
提供审计会话的创建、管理、持久化和恢复功能
"""
from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Callable


@dataclass
class AuditTurn:
    """审计轮次记录"""
    turn_id: str
    timestamp: float
    tool_name: str
    input_data: dict[str, Any]
    output_data: dict[str, Any]
    execution_time: float
    success: bool
    findings_count: int
    errors_count: int


@dataclass
class AuditUsage:
    """审计使用统计"""
    total_turns: int = 0
    total_findings: int = 0
    total_errors: int = 0
    total_execution_time: float = 0.0
    files_analyzed: int = 0
    lines_analyzed: int = 0


@dataclass
class AuditSessionConfig:
    """审计会话配置"""
    max_turns: int = 1000
    max_execution_time: float = 3600.0  # 1小时
    compact_after_turns: int = 100
    auto_save: bool = True
    save_interval: int = 10  # 每N轮自动保存


@dataclass
class AuditSession:
    """审计会话"""
    session_id: str
    project_path: str
    created_at: float
    updated_at: float
    config: AuditSessionConfig
    turns: list[AuditTurn] = field(default_factory=list)
    usage: AuditUsage = field(default_factory=AuditUsage)
    metadata: dict[str, Any] = field(default_factory=dict)
    status: str = "active"  # active, paused, completed, failed
    
    def __post_init__(self):
        if not self.session_id:
            self.session_id = uuid.uuid4().hex
        if not self.created_at:
            self.created_at = time.time()
        if not self.updated_at:
            self.updated_at = self.created_at
    
    def add_turn(self, turn: AuditTurn) -> None:
        """添加审计轮次"""
        self.turns.append(turn)
        self.updated_at = time.time()
        
        # 更新使用统计
        self.usage.total_turns += 1
        self.usage.total_findings += turn.findings_count
        self.usage.total_errors += turn.errors_count
        self.usage.total_execution_time += turn.execution_time
        
        # 自动压缩
        if len(self.turns) > self.config.compact_after_turns:
            self.compact_turns()
        
        # 自动保存
        if self.config.auto_save and self.usage.total_turns % self.config.save_interval == 0:
            self.save()
    
    def compact_turns(self, keep_last: int = 50) -> None:
        """压缩审计轮次，保留最近的N轮"""
        if len(self.turns) > keep_last:
            self.turns = self.turns[-keep_last:]
    
    def get_recent_turns(self, limit: int = 10) -> list[AuditTurn]:
        """获取最近的审计轮次"""
        return self.turns[-limit:]
    
    def get_turns_by_tool(self, tool_name: str) -> list[AuditTurn]:
        """根据工具名称获取审计轮次"""
        return [turn for turn in self.turns if turn.tool_name == tool_name]
    
    def get_failed_turns(self) -> list[AuditTurn]:
        """获取失败的审计轮次"""
        return [turn for turn in self.turns if not turn.success]
    
    def get_summary(self) -> dict[str, Any]:
        """获取会话摘要"""
        return {
            'session_id': self.session_id,
            'project_path': self.project_path,
            'created_at': datetime.fromtimestamp(self.created_at).isoformat(),
            'updated_at': datetime.fromtimestamp(self.updated_at).isoformat(),
            'status': self.status,
            'usage': asdict(self.usage),
            'turn_count': len(self.turns),
            'metadata': self.metadata
        }
    
    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            'session_id': self.session_id,
            'project_path': self.project_path,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'config': asdict(self.config),
            'turns': [asdict(turn) for turn in self.turns],
            'usage': asdict(self.usage),
            'metadata': self.metadata,
            'status': self.status
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'AuditSession':
        """从字典创建会话"""
        turns = [AuditTurn(**turn_data) for turn_data in data.get('turns', [])]
        config_data = data.get('config', {})
        config = AuditSessionConfig(**config_data) if config_data else AuditSessionConfig()
        usage_data = data.get('usage', {})
        usage = AuditUsage(**usage_data) if usage_data else AuditUsage()
        
        return cls(
            session_id=data['session_id'],
            project_path=data['project_path'],
            created_at=data['created_at'],
            updated_at=data['updated_at'],
            config=config,
            turns=turns,
            usage=usage,
            metadata=data.get('metadata', {}),
            status=data.get('status', 'active')
        )


class AuditSessionManager:
    """审计会话管理器"""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path("workspace/sessions")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._active_sessions: dict[str, AuditSession] = {}
    
    def create_session(
        self,
        project_path: str,
        config: Optional[AuditSessionConfig] = None,
        metadata: Optional[dict[str, Any]] = None
    ) -> AuditSession:
        """创建新的审计会话"""
        session = AuditSession(
            session_id=uuid.uuid4().hex,
            project_path=project_path,
            created_at=time.time(),
            updated_at=time.time(),
            config=config or AuditSessionConfig(),
            metadata=metadata or {}
        )
        
        self._active_sessions[session.session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[AuditSession]:
        """获取审计会话"""
        # 首先检查活跃会话
        if session_id in self._active_sessions:
            return self._active_sessions[session_id]
        
        # 尝试从存储加载
        return self.load_session(session_id)
    
    def load_session(self, session_id: str) -> Optional[AuditSession]:
        """从存储加载审计会话"""
        session_file = self.storage_path / f"{session_id}.json"
        
        if not session_file.exists():
            return None
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            session = AuditSession.from_dict(data)
            self._active_sessions[session_id] = session
            return session
            
        except Exception as e:
            print(f"Error loading session {session_id}: {e}")
            return None
    
    def save_session(self, session: AuditSession) -> bool:
        """保存审计会话"""
        try:
            session_file = self.storage_path / f"{session.session_id}.json"
            
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error saving session {session.session_id}: {e}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        """删除审计会话"""
        # 从活跃会话中移除
        if session_id in self._active_sessions:
            del self._active_sessions[session_id]
        
        # 删除存储文件
        session_file = self.storage_path / f"{session_id}.json"
        if session_file.exists():
            try:
                session_file.unlink()
                return True
            except Exception as e:
                print(f"Error deleting session {session_id}: {e}")
                return False
        
        return False
    
    def list_sessions(self, status: Optional[str] = None) -> list[AuditSession]:
        """列出审计会话"""
        sessions = []
        
        # 列出活跃会话
        for session in self._active_sessions.values():
            if status is None or session.status == status:
                sessions.append(session)
        
        # 列出存储的会话
        for session_file in self.storage_path.glob("*.json"):
            session_id = session_file.stem
            if session_id not in self._active_sessions:
                session = self.load_session(session_id)
                if session and (status is None or session.status == status):
                    sessions.append(session)
        
        # 按更新时间排序
        sessions.sort(key=lambda s: s.updated_at, reverse=True)
        return sessions
    
    def get_active_sessions(self) -> list[AuditSession]:
        """获取活跃会话"""
        return [session for session in self._active_sessions.values() if session.status == "active"]
    
    def cleanup_old_sessions(self, max_age_days: int = 30) -> int:
        """清理旧会话"""
        cutoff_time = time.time() - (max_age_days * 24 * 3600)
        cleaned_count = 0
        
        for session_file in self.storage_path.glob("*.json"):
            try:
                file_mtime = session_file.stat().st_mtime
                if file_mtime < cutoff_time:
                    session_file.unlink()
                    cleaned_count += 1
            except Exception as e:
                print(f"Error cleaning up session file {session_file}: {e}")
        
        return cleaned_count
    
    def get_session_statistics(self) -> dict[str, Any]:
        """获取会话统计信息"""
        all_sessions = self.list_sessions()
        
        total_sessions = len(all_sessions)
        active_sessions = len([s for s in all_sessions if s.status == "active"])
        completed_sessions = len([s for s in all_sessions if s.status == "completed"])
        failed_sessions = len([s for s in all_sessions if s.status == "failed"])
        
        total_findings = sum(s.usage.total_findings for s in all_sessions)
        total_errors = sum(s.usage.total_errors for s in all_sessions)
        total_files = sum(s.usage.files_analyzed for s in all_sessions)
        
        return {
            'total_sessions': total_sessions,
            'active_sessions': active_sessions,
            'completed_sessions': completed_sessions,
            'failed_sessions': failed_sessions,
            'total_findings': total_findings,
            'total_errors': total_errors,
            'total_files_analyzed': total_files,
            'storage_path': str(self.storage_path)
        }


# 创建全局会话管理器
audit_session_manager = AuditSessionManager()


def create_audit_turn(
    tool_name: str,
    input_data: dict[str, Any],
    output_data: dict[str, Any],
    execution_time: float,
    success: bool
) -> AuditTurn:
    """创建审计轮次记录"""
    findings_count = len(output_data.get('findings', []))
    errors_count = len(output_data.get('errors', []))
    
    return AuditTurn(
        turn_id=uuid.uuid4().hex,
        timestamp=time.time(),
        tool_name=tool_name,
        input_data=input_data,
        output_data=output_data,
        execution_time=execution_time,
        success=success,
        findings_count=findings_count,
        errors_count=errors_count
    )
