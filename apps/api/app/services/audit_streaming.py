"""
审计流式输出 - 借鉴claw-code的流式输出架构
提供实时审计进度反馈和结果流式传输
"""
from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Optional, AsyncGenerator, Callable


class AuditEventType(Enum):
    """审计事件类型"""
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    TOOL_START = "tool_start"
    TOOL_PROGRESS = "tool_progress"
    TOOL_END = "tool_end"
    FINDING = "finding"
    ERROR = "error"
    PROGRESS_UPDATE = "progress_update"
    STATUS_CHANGE = "status_change"


@dataclass
class AuditEvent:
    """审计事件"""
    event_type: AuditEventType
    timestamp: float
    session_id: str
    data: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps({
            'event_type': self.event_type.value,
            'timestamp': self.timestamp,
            'session_id': self.session_id,
            'data': self.data,
            'metadata': self.metadata
        }, ensure_ascii=False)
    
    def to_sse(self) -> str:
        """转换为Server-Sent Events格式"""
        return f"data: {self.to_json()}\n\n"


@dataclass
class AuditProgress:
    """审计进度"""
    total_files: int = 0
    processed_files: int = 0
    total_findings: int = 0
    current_file: str = ""
    current_tool: str = ""
    status: str = "idle"
    start_time: float = 0.0
    elapsed_time: float = 0.0
    
    def update_elapsed(self) -> None:
        """更新已用时间"""
        if self.start_time > 0:
            self.elapsed_time = time.time() - self.start_time
    
    def get_progress_percentage(self) -> float:
        """获取进度百分比"""
        if self.total_files == 0:
            return 0.0
        return (self.processed_files / self.total_files) * 100
    
    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return asdict(self)


class AuditStreamEmitter:
    """审计流发射器"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self._event_handlers: list[Callable[[AuditEvent], None]] = []
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._is_active = True
    
    def add_handler(self, handler: Callable[[AuditEvent], None]) -> None:
        """添加事件处理器"""
        self._event_handlers.append(handler)
    
    def remove_handler(self, handler: Callable[[AuditEvent], None]) -> None:
        """移除事件处理器"""
        if handler in self._event_handlers:
            self._event_handlers.remove(handler)
    
    def emit(self, event_type: AuditEventType, data: dict[str, Any], metadata: Optional[dict[str, Any]] = None) -> None:
        """发射审计事件"""
        event = AuditEvent(
            event_type=event_type,
            timestamp=time.time(),
            session_id=self.session_id,
            data=data,
            metadata=metadata or {}
        )
        
        # 调用所有处理器
        for handler in self._event_handlers:
            try:
                handler(event)
            except Exception as e:
                print(f"Error in event handler: {e}")
        
        # 添加到队列
        try:
            self._event_queue.put_nowait(event)
        except asyncio.QueueFull:
            print("Event queue is full, dropping event")
    
    async def stream_events(self) -> AsyncGenerator[str, None]:
        """流式输出事件"""
        while self._is_active:
            try:
                event = await asyncio.wait_for(
                    self._event_queue.get(),
                    timeout=1.0
                )
                yield event.to_sse()
            except asyncio.TimeoutError:
                # 发送心跳
                yield ": heartbeat\n\n"
            except Exception as e:
                print(f"Error streaming events: {e}")
                break
    
    def close(self) -> None:
        """关闭流发射器"""
        self._is_active = False


class AuditStreamManager:
    """审计流管理器"""
    
    def __init__(self):
        self._emitters: dict[str, AuditStreamEmitter] = {}
        self._progress: dict[str, AuditProgress] = {}
    
    def create_emitter(self, session_id: str) -> AuditStreamEmitter:
        """创建流发射器"""
        emitter = AuditStreamEmitter(session_id)
        self._emitters[session_id] = emitter
        self._progress[session_id] = AuditProgress()
        return emitter
    
    def get_emitter(self, session_id: str) -> Optional[AuditStreamEmitter]:
        """获取流发射器"""
        return self._emitters.get(session_id)
    
    def get_progress(self, session_id: str) -> Optional[AuditProgress]:
        """获取审计进度"""
        return self._progress.get(session_id)
    
    def update_progress(self, session_id: str, **kwargs) -> None:
        """更新审计进度"""
        progress = self._progress.get(session_id)
        if progress:
            for key, value in kwargs.items():
                if hasattr(progress, key):
                    setattr(progress, key, value)
            progress.update_elapsed()
    
    def close_emitter(self, session_id: str) -> None:
        """关闭流发射器"""
        emitter = self._emitters.get(session_id)
        if emitter:
            emitter.close()
            del self._emitters[session_id]
        
        if session_id in self._progress:
            del self._progress[session_id]
    
    def emit_session_start(self, session_id: str, project_path: str, total_files: int) -> None:
        """发射会话开始事件"""
        emitter = self.get_emitter(session_id)
        if emitter:
            self.update_progress(
                session_id,
                total_files=total_files,
                status="running",
                start_time=time.time()
            )
            emitter.emit(
                AuditEventType.SESSION_START,
                {
                    'project_path': project_path,
                    'total_files': total_files
                }
            )
    
    def emit_session_end(self, session_id: str, summary: dict[str, Any]) -> None:
        """发射会话结束事件"""
        emitter = self.get_emitter(session_id)
        if emitter:
            self.update_progress(session_id, status="completed")
            emitter.emit(
                AuditEventType.SESSION_END,
                summary
            )
    
    def emit_tool_start(self, session_id: str, tool_name: str, file_path: str) -> None:
        """发射工具开始事件"""
        emitter = self.get_emitter(session_id)
        if emitter:
            self.update_progress(
                session_id,
                current_tool=tool_name,
                current_file=file_path
            )
            emitter.emit(
                AuditEventType.TOOL_START,
                {
                    'tool_name': tool_name,
                    'file_path': file_path
                }
            )
    
    def emit_tool_progress(self, session_id: str, tool_name: str, progress: float, message: str) -> None:
        """发射工具进度事件"""
        emitter = self.get_emitter(session_id)
        if emitter:
            emitter.emit(
                AuditEventType.TOOL_PROGRESS,
                {
                    'tool_name': tool_name,
                    'progress': progress,
                    'message': message
                }
            )
    
    def emit_tool_end(self, session_id: str, tool_name: str, findings_count: int, errors_count: int) -> None:
        """发射工具结束事件"""
        emitter = self.get_emitter(session_id)
        if emitter:
            progress = self.get_progress(session_id)
            if progress:
                self.update_progress(
                    session_id,
                    processed_files=progress.processed_files + 1,
                    total_findings=progress.total_findings + findings_count
                )
            
            emitter.emit(
                AuditEventType.TOOL_END,
                {
                    'tool_name': tool_name,
                    'findings_count': findings_count,
                    'errors_count': errors_count
                }
            )
    
    def emit_finding(self, session_id: str, finding: dict[str, Any]) -> None:
        """发射发现事件"""
        emitter = self.get_emitter(session_id)
        if emitter:
            emitter.emit(
                AuditEventType.FINDING,
                finding
            )
    
    def emit_error(self, session_id: str, error_message: str, context: Optional[dict[str, Any]] = None) -> None:
        """发射错误事件"""
        emitter = self.get_emitter(session_id)
        if emitter:
            emitter.emit(
                AuditEventType.ERROR,
                {
                    'error_message': error_message,
                    'context': context or {}
                }
            )
    
    def emit_progress_update(self, session_id: str) -> None:
        """发射进度更新事件"""
        emitter = self.get_emitter(session_id)
        progress = self.get_progress(session_id)
        
        if emitter and progress:
            emitter.emit(
                AuditEventType.PROGRESS_UPDATE,
                progress.to_dict()
            )


# 创建全局流管理器
audit_stream_manager = AuditStreamManager()


async def stream_audit_progress(session_id: str) -> AsyncGenerator[str, None]:
    """流式输出审计进度"""
    emitter = audit_stream_manager.get_emitter(session_id)
    if not emitter:
        yield f"data: {json.dumps({'error': 'Session not found'})}\n\n"
        return
    
    async for event_sse in emitter.stream_events():
        yield event_sse


def create_progress_callback(session_id: str) -> Callable[[str, float, str], None]:
    """创建进度回调函数"""
    def callback(tool_name: str, progress: float, message: str) -> None:
        audit_stream_manager.emit_tool_progress(session_id, tool_name, progress, message)
    return callback
