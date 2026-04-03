"""
GEO 智能优化平台 - 自定义异常
"""
from typing import Optional, Any


class GEOBaseException(Exception):
    """基础异常类"""

    def __init__(self, message: str, code: str = "GEO_ERROR", details: Optional[Any] = None):
        self.message = message
        self.code = code
        self.details = details
        super().__init__(self.message)


class AuthenticationError(GEOBaseException):
    """认证错误"""
    pass


class AuthorizationError(GEOBaseException):
    """授权错误"""
    pass


class ResourceNotFoundError(GEOBaseException):
    """资源不存在"""
    pass


class ValidationError(GEOBaseException):
    """数据验证错误"""
    pass


class ExternalAPIError(GEOBaseException):
    """外部API调用错误"""
    pass


class AIPlatformError(GEOBaseException):
    """AI平台错误"""
    pass


class ContentPolicyError(GEOBaseException):
    """内容策略违规"""
    pass


class RateLimitError(GEOBaseException):
    """请求频率超限"""
    pass


class DataImportError(GEOBaseException):
    """数据导入错误"""
    pass


class AttributionError(GEOBaseException):
    """归因计算错误"""
    pass


class MonitoringError(GEOBaseException):
    """监测服务错误"""
    pass


class StorageError(GEOBaseException):
    """存储服务错误"""
    pass
