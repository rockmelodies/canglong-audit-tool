"""
Canglong API Main Application
苍龙API主应用

This is the main entry point for the Canglong Code Audit API server.
这是苍龙代码审计API服务器的主入口点。

Features / 功能:
- FastAPI application setup with CORS middleware
  FastAPI应用设置，包含CORS中间件
- Router registration for all API modules
  所有API模块的路由注册
- Health check endpoint for monitoring
  健康检查端点用于监控

Security Notes / 安全说明:
- CORS configuration should be restricted in production
  CORS配置在生产环境中应该受到限制
- All routers include authentication where needed
  所有路由器在需要的地方都包含认证

Author: Canglong Audit Team
Version: 1.0.0
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.audits import router as audits_router
from app.routers.auth import router as auth_router
from app.routers.dashboard import router as dashboard_router
from app.routers.llm import router as llm_router
from app.routers.missions import router as missions_router
from app.routers.repos import router as repos_router
from app.routers.settings import router as settings_router
from app.routers.users import router as users_router

# Configure logging / 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan context manager.
    应用生命周期上下文管理器。
    
    Handles startup and shutdown events for the application.
    处理应用程序的启动和关闭事件。
    
    Startup / 启动:
    - Initialize database connections (if using a real database)
      初始化数据库连接（如果使用真实数据库）
    - Load configuration
      加载配置
    - Warm up caches
      预热缓存
    
    Shutdown / 关闭:
    - Close database connections
      关闭数据库连接
    - Clean up resources
      清理资源
    """
    logger.info("Starting Canglong API server... / 正在启动苍龙API服务器...")
    
    # Startup logic here / 此处添加启动逻辑
    # Example: Initialize database connection pool
    # 示例：初始化数据库连接池
    
    yield
    
    # Shutdown logic here / 此处添加关闭逻辑
    logger.info("Shutting down Canglong API server... / 正在关闭苍龙API服务器...")


# Create FastAPI application instance / 创建FastAPI应用实例
app = FastAPI(
    title="Canglong API",
    description="""
    ## Canglong Code Audit API
    ## 苍龙代码审计API
    
    Orchestration API for code audit, vulnerability research, and sandbox execution.
    用于代码审计、漏洞研究和沙箱执行的编排API。
    
    ### Features / 功能特性
    - **Code Auditing**: Automated code security analysis / 代码审计：自动化代码安全分析
    - **Vulnerability Detection**: Multi-pattern vulnerability scanning / 漏洞检测：多模式漏洞扫描
    - **LLM Integration**: AI-powered analysis capabilities / LLM集成：AI驱动的分析能力
    - **User Management**: Role-based access control / 用户管理：基于角色的访问控制
    - **API Keys**: Programmatic access support / API密钥：程序化访问支持
    
    ### Authentication / 认证
    Most endpoints require authentication via Bearer token or API Key.
    大多数端点需要通过Bearer令牌或API密钥进行认证。
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Configure CORS middleware / 配置CORS中间件
# SECURITY WARNING: In production, replace "*" with specific allowed origins
# 安全警告：在生产环境中，请将"*"替换为具体的允许来源
# Example for production / 生产环境示例:
# allow_origins=["https://your-domain.com", "https://app.your-domain.com"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure for production / TODO: 为生产环境配置
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Recommended additions for security / 推荐的安全增强
    # max_age=600,  # Cache preflight requests for 10 minutes / 缓存预检请求10分钟
    # expose_headers=["X-Total-Count"],  # Expose custom headers / 暴露自定义头
)

# Register API routers / 注册API路由器
# The order of registration determines the order in OpenAPI docs
# 注册顺序决定了OpenAPI文档中的顺序

# Dashboard and monitoring / 仪表板和监控
app.include_router(dashboard_router, tags=["Dashboard"])

# LLM integration / LLM集成
app.include_router(llm_router, tags=["LLM"])

# Mission management / 任务管理
app.include_router(missions_router, tags=["Missions"])

# Authentication / 认证
app.include_router(auth_router, tags=["Authentication"])

# Repository management / 仓库管理
app.include_router(repos_router, tags=["Repositories"])

# Audit operations / 审计操作
app.include_router(audits_router, tags=["Audits"])

# System settings / 系统设置
app.include_router(settings_router, tags=["Settings"])

# User management / 用户管理
app.include_router(users_router, tags=["User Management"])


@app.get(
    "/healthz",
    tags=["System"],
    summary="Health Check / 健康检查",
    description="Returns the health status of the API server. Used by load balancers and monitoring systems.",
    response_description="Health status of the server"
)
def healthcheck() -> dict[str, str]:
    """
    Health check endpoint for monitoring and load balancing.
    用于监控和负载均衡的健康检查端点。
    
    This endpoint is used by:
    此端点用于：
    - Kubernetes liveness/readiness probes
      Kubernetes存活/就绪探针
    - Load balancer health checks
      负载均衡器健康检查
    - Monitoring systems
      监控系统
    
    Returns:
        dict: Health status with "status" key
        dict: 包含"status"键的健康状态
    
    Example response / 响应示例:
        {"status": "ok"}
    """
    return {"status": "ok"}


@app.get(
    "/",
    tags=["System"],
    summary="API Root / API根路径",
    description="Returns basic information about the API",
    include_in_schema=False
)
def root() -> dict[str, str]:
    """
    Root endpoint providing API information.
    提供API信息的根端点。
    
    Returns:
        dict: Basic API information
        dict: 基本API信息
    """
    return {
        "name": "Canglong API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/healthz"
    }


# Exception handlers can be added here / 可以在此处添加异常处理器
# Example / 示例:
# @app.exception_handler(ValueError)
# async def value_error_handler(request: Request, exc: ValueError):
#     return JSONResponse(
#         status_code=400,
#         content={"detail": str(exc)}
#     )


if __name__ == "__main__":
    import uvicorn
    
    # Run the application with uvicorn / 使用uvicorn运行应用
    # This is for development only. In production, use a proper WSGI server.
    # 这仅用于开发。在生产环境中，请使用适当的WSGI服务器。
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development / 开发时启用自动重载
        log_level="info"
    )
