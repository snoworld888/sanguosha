"""
GEO 智能优化平台 - API路由初始化
"""
from fastapi import APIRouter

from src.api.routers import (
    auth,
    tenants,
    users,
    keywords,
    content,
    monitoring,
    analysis,
    attribution,
    health
)

# 导出路由
auth_router = auth.router
tenants_router = tenants.router
users_router = users.router
keywords_router = keywords.router
content_router = content.router
monitoring_router = monitoring.router
analysis_router = analysis.router
attribution_router = attribution.router
health_router = health.router

__all__ = [
    "auth_router",
    "tenants_router",
    "users_router",
    "keywords_router",
    "content_router",
    "monitoring_router",
    "analysis_router",
    "attribution_router",
    "health_router",
]
