"""
GEO 智能优化平台 - 核心配置模块
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List
import os


class Settings(BaseSettings):
    """应用配置"""

    # 应用信息
    APP_NAME: str = "GEO智能优化平台"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # 数据库配置
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/geo_platform"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: str = ""

    # Elasticsearch配置
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    ELASTICSEARCH_INDEX_PREFIX: str = "geo"

    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # AI模型配置
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_API_URL: str = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    VOLCANO_API_KEY: str = ""
    VOLCANO_ENDPOINT: str = "https://ark.cn-beijing.volces.com/api/v3"

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5"

    # 监测配置
    MONITORING_FREQUENCY: dict = {
        "hourly": 1,
        "daily": 24,
        "weekly": 168
    }

    # 支持的AI平台
    SUPPORTED_AI_PLATFORMS: List[str] = [
        "deepseek", "kimi", "doubao", "wenxin", "tongyi",
        "yuanbao", "chatgpt", "gemini", "claude"
    ]

    # 支持的内容平台
    SUPPORTED_CONTENT_PLATFORMS: List[str] = [
        "wechat", "zhihu", "xiaohongshu", "douyin", "bilibili"
    ]

    # 第三方API配置
    WECHAT_APP_ID: str = ""
    WECHAT_APP_SECRET: str = ""

    ZHUHU_CLIENT_ID: str = ""
    ZHUHU_CLIENT_SECRET: str = ""

    # 存储配置
    OSS_ENDPOINT: str = "oss-cn-beijing.aliyuncs.com"
    OSS_BUCKET: str = "geo-platform"
    OSS_ACCESS_KEY: str = ""
    OSS_ACCESS_SECRET: str = ""

    COS_ENDPOINT: str = "cos.ap-beijing.myqcloud.com"
    COS_BUCKET: str = "geo-platform"
    COS_SECRET_ID: str = ""
    COS_SECRET_KEY: str = ""

    # 阿里云/腾讯云切换
    CLOUD_PROVIDER: str = "aliyun"  # aliyun | tencent

    # 认证配置
    ALLOW_ORIGINS: List[str] = ["*"]
    ALLOW_METHODS: List[str] = ["*"]
    ALLOW_HEADERS: List[str] = ["*"]

    # 限流配置
    RATE_LIMIT_PER_MINUTE: int = 60

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()
