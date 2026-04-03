"""
GEO 智能优化平台 - SQLAlchemy 数据库模型
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import uuid
import enum

Base = declarative_base()


def generate_uuid():
    return str(uuid.uuid4())


class TenantPlan(str, enum.Enum):
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class MonitoringStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Tenant(Base):
    """租户表"""
    __tablename__ = "tenants"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    plan = Column(SQLEnum(TenantPlan), default=TenantPlan.STARTER)
    contact_email = Column(String(255), nullable=False)
    api_key = Column(String(255), unique=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    users = relationship("User", back_populates="tenant")
    keywords = relationship("Keyword", back_populates="tenant")
    content_sources = relationship("ContentSource", back_populates="tenant")
    monitoring_tasks = relationship("MonitoringTask", back_populates="tenant")
    citation_records = relationship("CitationRecord", back_populates="tenant")


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="operator")
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    last_login_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    tenant = relationship("Tenant", back_populates="users")


class Keyword(Base):
    """关键词表"""
    __tablename__ = "keywords"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False)
    brand_name = Column(String(100), nullable=False)
    synonyms = Column(JSON, default=list)
    competitors = Column(JSON, default=list)
    platforms = Column(JSON, default=list)
    frequency = Column(String(20), default="daily")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 索引
    __table_args__ = (
        Index("ix_keywords_tenant_id", "tenant_id"),
        Index("ix_keywords_brand_name", "brand_name"),
    )

    # 关系
    tenant = relationship("Tenant", back_populates="keywords")


class ContentSource(Base):
    """内容源表"""
    __tablename__ = "content_sources"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False)
    platform = Column(String(50), nullable=False)
    content_type = Column(String(50), nullable=False)
    content_id = Column(String(255))
    title = Column(String(500), nullable=False)
    summary = Column(Text)
    author = Column(String(255))
    author_id = Column(String(255))
    url = Column(String(1000))
    publish_time = Column(DateTime)
    metrics = Column(JSON, default=dict)
    ai_citation_details = Column(JSON, default=list)
    geo_tags = Column(JSON, default=list)
    gem_score = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 索引
    __table_args__ = (
        Index("ix_content_sources_tenant_id", "tenant_id"),
        Index("ix_content_sources_platform", "platform"),
        Index("ix_content_sources_content_id", "content_id"),
    )

    # 关系
    tenant = relationship("Tenant", back_populates="content_sources")
    citation_records = relationship("CitationRecord", back_populates="content_source")


class MonitoringTask(Base):
    """监测任务表"""
    __tablename__ = "monitoring_tasks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False)
    name = Column(String(200), nullable=False)
    keywords = Column(JSON, default=list)
    platforms = Column(JSON, default=list)
    frequency = Column(String(20), default="daily")
    status = Column(SQLEnum(MonitoringStatus), default=MonitoringStatus.PENDING)
    last_run_at = Column(DateTime)
    next_run_at = Column(DateTime)
    error_message = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 索引
    __table_args__ = (
        Index("ix_monitoring_tasks_tenant_id", "tenant_id"),
        Index("ix_monitoring_tasks_status", "status"),
    )

    # 关系
    tenant = relationship("Tenant", back_populates="monitoring_tasks")
    citation_records = relationship("CitationRecord", back_populates="monitoring_task")


class CitationRecord(Base):
    """引用记录表"""
    __tablename__ = "citation_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False)
    content_source_id = Column(String(36), ForeignKey("content_sources.id"))
    monitoring_task_id = Column(String(36), ForeignKey("monitoring_tasks.id"))
    ai_platform = Column(String(50), nullable=False)
    search_query = Column(String(500), nullable=False)
    citation_context = Column(Text)
    brand_keyword = Column(String(200))
    user_id = Column(String(36))
    citation_time = Column(DateTime, nullable=False)
    position = Column(Integer, default=0)
    confidence = Column(Float, default=0.0)
    created_at = Column(DateTime, server_default=func.now())

    # 索引
    __table_args__ = (
        Index("ix_citation_records_tenant_id", "tenant_id"),
        Index("ix_citation_records_ai_platform", "ai_platform"),
        Index("ix_citation_records_citation_time", "citation_time"),
        Index("ix_citation_records_brand_keyword", "brand_keyword"),
    )

    # 关系
    tenant = relationship("Tenant", back_populates="citation_records")
    content_source = relationship("ContentSource", back_populates="citation_records")
    monitoring_task = relationship("MonitoringTask", back_populates="citation_records")


class AnalysisReport(Base):
    """分析报告表"""
    __tablename__ = "analysis_reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), nullable=False)
    content_source_id = Column(String(36), ForeignKey("content_sources.id"))
    gem_score_total = Column(Float)
    gem_score_structure = Column(Float)
    gem_score_authority = Column(Float)
    gem_score_evidence = Column(Float)
    gem_score_expression = Column(Float)
    gem_score_perspective = Column(Float)
    diagnosis_content_gaps = Column(JSON, default=list)
    diagnosis_structure_suggestions = Column(JSON, default=list)
    diagnosis_authority_improvements = Column(JSON, default=list)
    diagnosis_competitor_gaps = Column(JSON, default=dict)
    created_at = Column(DateTime, server_default=func.now())

    # 索引
    __table_args__ = (
        Index("ix_analysis_reports_tenant_id", "tenant_id"),
        Index("ix_analysis_reports_content_source_id", "content_source_id"),
    )


class AttributionEvent(Base):
    """归因事件表"""
    __tablename__ = "attribution_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), nullable=False)
    user_identifier = Column(String(255), nullable=False)
    event_type = Column(String(100), nullable=False)
    channel = Column(String(100))
    campaign = Column(String(255))
    event_time = Column(DateTime, nullable=False)
    properties = Column(JSON, default=dict)
    created_at = Column(DateTime, server_default=func.now())

    # 索引
    __table_args__ = (
        Index("ix_attribution_events_tenant_id", "tenant_id"),
        Index("ix_attribution_events_user_identifier", "user_identifier"),
        Index("ix_attribution_events_event_time", "event_time"),
    )
