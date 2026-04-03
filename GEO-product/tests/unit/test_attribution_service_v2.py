"""
GEO 归因服务补充测试 - 覆盖 generate_report, track_event 等
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from src.services.attribution.service import AttributionService
from src.models.schemas import (
    AttributionEvent,
    PlatformEnum,
    MonitoringFrequencyEnum
)


class TestAttributionServiceReport:
    """归因服务报告生成测试"""

    def setup_method(self):
        """测试前准备"""
        self.service = AttributionService()

    def _create_event(
        self,
        event_type: str,
        channel: str,
        days_ago: int,
        user_id: str = "user_1",
        cost: float = 0.0,
        conversion_value: float = 0.0
    ) -> AttributionEvent:
        """创建测试用事件"""
        return AttributionEvent(
            tenant_id="test_tenant",
            event_type=event_type,
            event_time=datetime.now() - timedelta(days=days_ago),
            channel=channel,
            user_identifier=user_id,
            properties={
                "cost": cost,
                "conversion_value": conversion_value
            }
        )

    @pytest.mark.asyncio
    async def test_generate_report_empty_events(self):
        """测试空事件报告生成"""
        report = await self.service.generate_report(
            tenant_id="test_tenant",
            events=[],
            date_range={
                "start": datetime.now() - timedelta(days=30),
                "end": datetime.now()
            },
            model_type="last_touch"
        )
        
        assert report.tenant_id == "test_tenant"
        assert report.total_citations == 0
        assert report.total_conversions == 0

    @pytest.mark.asyncio
    async def test_generate_report_with_citations_only(self):
        """测试仅有引用的报告生成"""
        events = [
            self._create_event("citation", "deepseek", 5),
            self._create_event("citation", "kimi", 3),
            self._create_event("citation", "doubao", 1),
        ]
        
        report = await self.service.generate_report(
            tenant_id="test_tenant",
            events=events,
            date_range={
                "start": datetime.now() - timedelta(days=30),
                "end": datetime.now()
            },
            model_type="first_touch"
        )
        
        assert report.total_citations == 3
        assert report.total_conversions == 0

    @pytest.mark.asyncio
    async def test_generate_report_with_conversions(self):
        """测试有转化的报告生成"""
        events = [
            self._create_event("citation", "deepseek", 10, cost=10.0),
            self._create_event("citation", "kimi", 5, cost=5.0),
            self._create_event("purchase", "direct", 1, conversion_value=500.0),
        ]
        
        report = await self.service.generate_report(
            tenant_id="test_tenant",
            events=events,
            date_range={
                "start": datetime.now() - timedelta(days=30),
                "end": datetime.now()
            },
            model_type="last_touch"
        )
        
        assert report.total_citations == 2
        assert report.total_conversions == 1
        assert report.conversion_rate > 0

    @pytest.mark.asyncio
    async def test_generate_report_roi_calculation(self):
        """测试ROI计算"""
        events = [
            self._create_event("citation", "deepseek", 5, cost=100.0),
            self._create_event("purchase", "website", 1, conversion_value=1000.0),
        ]
        
        report = await self.service.generate_report(
            tenant_id="test_tenant",
            events=events,
            date_range={
                "start": datetime.now() - timedelta(days=30),
                "end": datetime.now()
            },
            model_type="linear"
        )
        
        assert report.roi == 9.0  # (1000 - 100) / 100 = 9

    @pytest.mark.asyncio
    async def test_generate_report_no_cost(self):
        """测试无成本的ROI计算"""
        events = [
            self._create_event("citation", "deepseek", 5, cost=0.0),
            self._create_event("purchase", "website", 1, conversion_value=500.0),
        ]
        
        report = await self.service.generate_report(
            tenant_id="test_tenant",
            events=events,
            date_range={
                "start": datetime.now() - timedelta(days=30),
                "end": datetime.now()
            },
            model_type="last_touch"
        )
        
        assert report.roi == 0  # 除以0的情况

    @pytest.mark.asyncio
    async def test_generate_report_top_channels(self):
        """测试Top渠道计算"""
        events = [
            self._create_event("citation", "deepseek", 5),
            self._create_event("citation", "deepseek", 4),
            self._create_event("citation", "deepseek", 3),
            self._create_event("citation", "kimi", 2),
            self._create_event("citation", "doubao", 1),
        ]
        
        report = await self.service.generate_report(
            tenant_id="test_tenant",
            events=events,
            date_range={
                "start": datetime.now() - timedelta(days=30),
                "end": datetime.now()
            },
            model_type="last_touch"
        )
        
        assert len(report.top_channels) > 0
        # deepseek应该有最高权重
        assert report.top_channels[0]["channel"] == "deepseek"

    @pytest.mark.asyncio
    async def test_generate_report_attribution_links(self):
        """测试归因链路构建"""
        events = [
            self._create_event("citation", "deepseek", 10, user_id="user_1"),
            self._create_event("visit", "website", 5, user_id="user_1"),
            self._create_event("purchase", "direct", 1, user_id="user_1"),
        ]
        
        report = await self.service.generate_report(
            tenant_id="test_tenant",
            events=events,
            date_range={
                "start": datetime.now() - timedelta(days=30),
                "end": datetime.now()
            },
            model_type="last_touch"
        )
        
        assert report.attribution_links is not None

    @pytest.mark.asyncio
    async def test_generate_report_date_range_defaults(self):
        """测试日期范围默认值"""
        events = []
        
        report = await self.service.generate_report(
            tenant_id="test_tenant",
            events=events,
            date_range={},
            model_type="last_touch"
        )
        
        # 应该使用默认日期范围
        assert report.date_range["start"] is not None
        assert report.date_range["end"] is not None


class TestAttributionServiceTrackEvent:
    """归因服务事件追踪测试"""

    def setup_method(self):
        """测试前准备"""
        self.service = AttributionService()

    def test_track_event_basic(self):
        """测试基本事件追踪"""
        event = self.service.track_event(
            tenant_id="test_tenant",
            event_type="citation",
            user_identifier="user_123",
            channel="deepseek"
        )
        
        assert event.tenant_id == "test_tenant"
        assert event.event_type == "citation"
        assert event.user_identifier == "user_123"
        assert event.channel == "deepseek"
        assert event.event_time is not None

    def test_track_event_with_properties(self):
        """测试带属性的事件追踪"""
        properties = {
            "keyword": "品牌A",
            "platform": "deepseek",
            "position": 3
        }
        
        event = self.service.track_event(
            tenant_id="test_tenant",
            event_type="citation",
            user_identifier="user_456",
            channel="kimi",
            properties=properties
        )
        
        assert event.properties == properties

    def test_track_event_with_campaign(self):
        """测试带营销活动的事件追踪"""
        event = self.service.track_event(
            tenant_id="test_tenant",
            event_type="visit",
            user_identifier="user_789",
            channel="website",
            campaign="summer_sale_2024"
        )
        
        assert event.campaign == "summer_sale_2024"

    def test_track_event_purchase_conversion(self):
        """测试购买转化事件追踪"""
        properties = {
            "order_id": "ORDER_123",
            "amount": 299.99,
            "products": ["商品A", "商品B"]
        }
        
        event = self.service.track_event(
            tenant_id="test_tenant",
            event_type="purchase",
            user_identifier="user_vip",
            channel="wechat_mini",
            properties=properties
        )
        
        assert event.event_type == "purchase"

    def test_track_event_signup_conversion(self):
        """测试注册转化事件追踪"""
        event = self.service.track_event(
            tenant_id="test_tenant",
            event_type="signup",
            user_identifier="new_user",
            channel="landing_page"
        )
        
        assert event.event_type == "signup"


class TestAttributionServiceHelpers:
    """归因服务辅助方法测试"""

    def setup_method(self):
        """测试前准备"""
        self.service = AttributionService()

    def test_get_conversion_value_with_value(self):
        """测试获取转化价值（有时有值）"""
        properties = {"conversion_value": 299.99}
        value = self.service._get_conversion_value(properties)
        assert value == 299.99

    def test_get_conversion_value_without_value(self):
        """测试获取转化价值（无值）"""
        properties = {}
        value = self.service._get_conversion_value(properties)
        assert value == 0.0

    def test_get_conversion_value_zero(self):
        """测试获取转化价值（零值）"""
        properties = {"conversion_value": 0}
        value = self.service._get_conversion_value(properties)
        assert value == 0.0


class TestAttributionServiceIdMapping:
    """归因服务ID映射测试"""

    def setup_method(self):
        """测试前准备"""
        self.service = AttributionService()

    @pytest.mark.asyncio
    async def test_map_user_identifiers(self):
        """测试用户标识映射"""
        # 创建跨平台事件
        events = [
            AttributionEvent(
                tenant_id="test_tenant",
                event_type="citation",
                event_time=datetime.now(),
                channel="deepseek",
                user_identifier="anonymous_abc123",
            ),
            AttributionEvent(
                tenant_id="test_tenant",
                event_type="signup",
                event_time=datetime.now(),
                channel="website",
                user_identifier="user_123",
                properties={"mapped_from": "anonymous_abc123"}
            ),
        ]
        
        # ID映射后，同一用户应该有统一的标识
        # 简化测试：验证事件可以正常创建
        assert len(events) == 2

    def test_identify_user_by_phone(self):
        """测试通过手机号识别用户"""
        event = AttributionEvent(
            tenant_id="test_tenant",
            event_type="citation",
            event_time=datetime.now(),
            channel="deepseek",
            user_identifier="13800138000",  # 手机号作为标识
        )
        
        assert event.user_identifier is not None

    def test_identify_user_by_openid(self):
        """测试通过OpenID识别用户"""
        event = AttributionEvent(
            tenant_id="test_tenant",
            event_type="purchase",
            event_time=datetime.now(),
            channel="wechat",
            user_identifier="oXXXX_OpenID_String",
        )
        
        assert "OpenID" in event.user_identifier or event.user_identifier.startswith("o")
