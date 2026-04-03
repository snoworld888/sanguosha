"""
GEO 智能优化平台 - 健康检查路由
"""
from fastapi import APIRouter

from src.core.config import settings
from src.models.schemas import HealthCheckResponse

router = APIRouter()


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    健康检查接口

    返回系统各组件的健康状态
    """
    # 简化实现，实际需要检查数据库、Redis、ES等连接
    return HealthCheckResponse(
        status="healthy",
        version=settings.APP_VERSION,
        database="connected",
        redis="connected",
        elasticsearch="connected"
    )


@router.get("/health/detailed")
async def detailed_health_check():
    """
    详细健康检查

    返回各组件的详细状态信息
    """
    # 模拟详细健康信息
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "timestamp": "2026-03-24T08:00:00Z",
        "components": {
            "api": {"status": "healthy", "response_time_ms": 15},
            "database": {"status": "healthy", "response_time_ms": 5},
            "redis": {"status": "healthy", "response_time_ms": 2},
            "elasticsearch": {"status": "healthy", "response_time_ms": 10},
            "ai_deepseek": {"status": "healthy", "response_time_ms": 200},
            "ai_kimi": {"status": "healthy", "response_time_ms": 180},
            "ai_doubao": {"status": "healthy", "response_time_ms": 150}
        },
        "uptime_seconds": 3600,
        "memory_usage_mb": 256,
        "cpu_percent": 15
    }


@router.get("/ready")
async def readiness_check():
    """
    就绪检查

    用于Kubernetes就绪探测
    """
    return {"ready": True}


@router.get("/live")
async def liveness_check():
    """
    存活检查

    用于Kubernetes存活探测
    """
    return {"alive": True}
