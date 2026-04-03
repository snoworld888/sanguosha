"""
GEO 智能优化平台 - Pydantic 数据模型
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class PlatformEnum(str, Enum):
    """平台枚举"""
    # AI平台
    DEEPSEEK = "deepseek"
    KIMI = "kimi"
    DOUBAO = "doubao"
    WENXIN = "wenxin"
    TONGYI = "tongyi"
    YUANBAO = "yuanbao"
    CHATGPT = "chatgpt"
    GEMINI = "gemini"
    CLAUDE = "claude"

    # 内容平台
    WECHAT = "wechat"
    ZHUHU = "zhihu"
    XIAOHONGSHU = "xiaohongshu"
    DOUYIN = "douyin"
    BILIBILI = "bilibili"


class ContentTypeEnum(str, Enum):
    """内容类型枚举"""
    ARTICLE = "article"
    ANSWER = "answer"
    NOTE = "note"
    VIDEO = "video"
    SHORT_VIDEO = "short_video"


class MonitoringFrequencyEnum(str, Enum):
    """监测频率枚举"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"


class TenantPlanEnum(str, Enum):
    """租户套餐枚举"""
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


# ===== 租户相关模型 =====

class TenantBase(BaseModel):
    """租户基础模型"""
    name: str = Field(..., min_length=1, max_length=100)
    plan: TenantPlanEnum = TenantPlanEnum.STARTER
    contact_email: str = Field(..., pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


class TenantCreate(TenantBase):
    """创建租户"""
    pass


class Tenant(TenantBase):
    """租户响应"""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== 用户相关模型 =====

class UserBase(BaseModel):
    """用户基础模型"""
    email: str
    username: str
    role: str = "operator"


class UserCreate(UserBase):
    """创建用户"""
    password: str = Field(..., min_length=8)
    tenant_id: str


class User(UserBase):
    """用户响应"""
    id: str
    tenant_id: str
    is_active: bool = True
    created_at: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """登录请求"""
    email: str
    password: str


class TokenResponse(BaseModel):
    """令牌响应"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


# ===== 关键词监测模型 =====

class KeywordBase(BaseModel):
    """关键词基础模型"""
    brand_name: str
    synonyms: List[str] = []
    competitors: List[str] = []


class KeywordCreate(KeywordBase):
    """创建关键词"""
    tenant_id: str
    platforms: List[PlatformEnum] = [PlatformEnum.DEEPSEEK, PlatformEnum.KIMI]
    frequency: MonitoringFrequencyEnum = MonitoringFrequencyEnum.DAILY


class Keyword(KeywordBase):
    """关键词响应"""
    id: str
    tenant_id: str
    platforms: List[str]
    frequency: str
    is_active: bool = True
    created_at: datetime

    class Config:
        from_attributes = True


# ===== 内容源模型 =====

class ContentMetrics(BaseModel):
    """内容指标"""
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    ai_citations: int = 0


class AICitationDetail(BaseModel):
    """AI引用详情"""
    ai_platform: PlatformEnum
    citation_time: datetime
    citation_context: str
    search_query: str


class ContentSourceBase(BaseModel):
    """内容源基础模型"""
    platform: PlatformEnum
    content_type: ContentTypeEnum
    title: str
    summary: Optional[str] = None
    url: str
    author: str
    author_id: Optional[str] = None


class ContentSourceCreate(ContentSourceBase):
    """创建内容源"""
    tenant_id: str
    content_id: Optional[str] = None
    publish_time: Optional[datetime] = None
    metrics: ContentMetrics = Field(default_factory=ContentMetrics)


class ContentSource(ContentSourceBase):
    """内容源响应"""
    id: str
    tenant_id: str
    content_id: Optional[str]
    publish_time: Optional[datetime]
    metrics: ContentMetrics
    ai_citation_details: List[AICitationDetail] = []
    geo_tags: List[str] = []
    gem_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== 监测任务模型 =====

class MonitoringTaskBase(BaseModel):
    """监测任务基础模型"""
    name: str
    keywords: List[str]
    platforms: List[PlatformEnum]
    frequency: MonitoringFrequencyEnum


class MonitoringTaskCreate(MonitoringTaskBase):
    """创建监测任务"""
    tenant_id: str


class MonitoringTask(MonitoringTaskBase):
    """监测任务响应"""
    id: str
    tenant_id: str
    status: str = "pending"
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ===== 引用记录模型 =====

class CitationRecordBase(BaseModel):
    """引用记录基础模型"""
    ai_platform: PlatformEnum
    search_query: str
    citation_context: str
    brand_keyword: str


class CitationRecordCreate(CitationRecordBase):
    """创建引用记录"""
    tenant_id: str
    content_source_id: Optional[str] = None


class CitationRecord(CitationRecordBase):
    """引用记录响应"""
    id: str
    tenant_id: str
    content_source_id: Optional[str]
    user_id: Optional[str] = None
    citation_time: datetime
    position: int = 0
    confidence: float = 0.0
    created_at: datetime

    class Config:
        from_attributes = True


# ===== 分析报告模型 =====

class GEMScore(BaseModel):
    """GEM评分"""
    total: float = Field(..., ge=0, le=100)
    structure: float = Field(..., ge=0, le=100)
    authority: float = Field(..., ge=0, le=100)
    evidence: float = Field(..., ge=0, le=100)
    expression: float = Field(..., ge=0, le=100)
    perspective: float = Field(..., ge=0, le=100)


class DiagnosisReport(BaseModel):
    """诊断报告"""
    content_gaps: List[str] = []
    structure_suggestions: List[str] = []
    authority_improvements: List[str] = []
    competitor_gaps: Dict[str, Any] = {}


class AnalysisReport(BaseModel):
    """分析报告响应"""
    id: str
    tenant_id: str
    content_source_id: str
    gem_score: GEMScore
    diagnosis: DiagnosisReport
    created_at: datetime

    class Config:
        from_attributes = True


# ===== 内容生成模型 =====

class ContentGenerationRequest(BaseModel):
    """内容生成请求"""
    platform: PlatformEnum
    content_type: ContentTypeEnum
    topic: str
    keywords: List[str] = []
    tone: str = "professional"
    length: int = Field(default=1000, ge=500, le=5000)
    include_cover: bool = True


class GeneratedContent(BaseModel):
    """生成的内容"""
    title: str
    body: str
    cover_url: Optional[str] = None
    tags: List[str] = []
    estimated_read_time: int = 0
    seo_suggestions: List[str] = []


class ContentGenerationResponse(BaseModel):
    """内容生成响应"""
    request_id: str
    content: GeneratedContent
    quality_score: float
    warnings: List[str] = []


# ===== 归因分析模型 =====

class AttributionEvent(BaseModel):
    """归因事件"""
    tenant_id: str
    event_type: str
    event_time: datetime
    channel: str
    campaign: Optional[str] = None
    user_identifier: str
    properties: Dict[str, Any] = {}


class AttributionLink(BaseModel):
    """归因链路"""
    events: List[AttributionEvent]
    total_touchpoints: int
    attributed_conversion_value: float
    attribution_model: str = "last_click"


class AttributionReport(BaseModel):
    """归因报告"""
    id: str
    tenant_id: str
    date_range: Dict[str, datetime]
    total_citations: int
    total_conversions: int
    conversion_rate: float
    roi: float
    top_channels: List[Dict[str, Any]] = []
    attribution_links: List[AttributionLink] = []
    created_at: datetime

    class Config:
        from_attributes = True


# ===== 通用响应模型 =====

class PaginatedResponse(BaseModel):
    """分页响应"""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


class HealthCheckResponse(BaseModel):
    """健康检查响应"""
    status: str
    version: str
    database: str
    redis: str
    elasticsearch: str
