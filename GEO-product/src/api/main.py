"""
GEO 智能优化平台 - FastAPI 应用入口
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager

from src.core.config import settings
from src.core.exceptions import GEOBaseException
from src.api.routers import (
    auth_router,
    tenants_router,
    users_router,
    keywords_router,
    content_router,
    monitoring_router,
    analysis_router,
    attribution_router,
    health_router
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} 启动中...")
    yield
    # 关闭时执行
    print("👋 应用关闭")


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## GEO 智能优化平台 API

国内首个全栈自研的生成式引擎优化 SaaS 系统 API。

### 主要功能

- 🤖 **AI平台监测** - 实时监测 DeepSeek/Kimi/豆包等平台的品牌引用情况
- 📊 **智能分析** - GEM评分模型、引用特征分析、竞品差距诊断
- ✍️ **内容生成** - 多平台 GEO 优化内容自动生成
- 🔗 **ROI归因** - 跨平台 ID-Mapping，全链路转化追踪
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.ALLOW_METHODS,
    allow_headers=settings.ALLOW_HEADERS,
)


# 异常处理器
@app.exception_handler(GEOBaseException)
async def geo_exception_handler(request: Request, exc: GEOBaseException):
    """自定义业务异常处理"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "code": exc.code,
            "message": exc.message,
            "details": exc.details
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证异常处理"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": "VALIDATION_ERROR",
            "message": "请求参数验证失败",
            "details": exc.errors()
        }
    )


# 注册路由
app.include_router(health_router, prefix="/api/v1", tags=["健康检查"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(tenants_router, prefix="/api/v1/tenants", tags=["租户管理"])
app.include_router(users_router, prefix="/api/v1/users", tags=["用户管理"])
app.include_router(keywords_router, prefix="/api/v1/keywords", tags=["关键词管理"])
app.include_router(content_router, prefix="/api/v1/content", tags=["内容管理"])
app.include_router(monitoring_router, prefix="/api/v1/monitoring", tags=["监测服务"])
app.include_router(analysis_router, prefix="/api/v1/analysis", tags=["分析服务"])
app.include_router(attribution_router, prefix="/api/v1/attribution", tags=["归因服务"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
