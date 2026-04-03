"""
GEO 智能优化平台 - 归因服务单元测试
"""
import pytest
from datetime import datetime, timedelta
from src.services.attribution import (
    AttributionService,
    AttributionModel,
    IDMappingService
)
from src.models.schemas import AttributionEvent


class TestAttributionModel:
    """归因模型测试"""

    def setup_method(self):
        """测试前准备"""
        self.model = AttributionModel()
        self.now = datetime.now()

    def _create_events(self, count=5):
        """创建测试事件"""
        events = []
        channels = ["deepseek", "kimi", "wechat"]

        for i in range(count):
            event = AttributionEvent(
                tenant_id="t1",
                user_identifier=f"user_{i % 2}",  # 2个用户
                event_type="citation" if i % 3 != 0 else "conversion",
                channel=channels[i % 3],
                event_time=self.now - timedelta(hours=count - i),
                properties={"conversion_value": 100 if i % 3 == 0 else 0}
            )
            events.append(event)

        return events

    def test_first_touch_attribution(self):
        """测试首次触点归因"""
        events = self._create_events(5)
        result = self.model.first_touch(events)

        assert isinstance(result, dict)
        # 验证归因权重分配
        assert sum(result.values()) > 0

    def test_last_touch_attribution(self):
        """测试末次触点归因"""
        events = self._create_events(5)
        result = self.model.last_touch(events)

        assert isinstance(result, dict)
        assert sum(result.values()) > 0

    def test_linear_attribution(self):
        """测试线性归因"""
        events = self._create_events(4)
        result = self.model.linear(events)

        assert isinstance(result, dict)
        assert sum(result.values()) > 0

        # 线性归因应该平均分配
        if len(result) > 1:
            values = list(result.values())
            # 不应该差距太大
            max_diff = max(values) - min(values)
            assert max_diff < 200  # 因为转化事件价值为100

    def test_time_decay_attribution(self):
        """测试时间衰减归因"""
        events = self._create_events(6)
        result = self.model.time_decay(events, half_life_hours=24)

        assert isinstance(result, dict)
        assert sum(result.values()) > 0

    def test_empty_events(self):
        """测试空事件列表"""
        events = []

        assert self.model.first_touch(events) == {}
        assert self.model.last_touch(events) == {}
        assert self.model.linear(events) == {}

    def test_single_channel(self):
        """测试单一渠道"""
        event = AttributionEvent(
            tenant_id="t1",
            user_identifier="user_1",
            event_type="conversion",
            channel="deepseek",
            event_time=self.now,
            properties={"conversion_value": 100}
        )

        result = self.model.first_touch([event])
        assert result.get("deepseek") == 100

    def test_custom_attribution(self):
        """测试自定义归因"""
        events = self._create_events(4)
        weights = {"deepseek": 0.5, "kimi": 0.3, "wechat": 0.2}

        result = self.model.custom(events, weights)

        assert isinstance(result, dict)


class TestIDMappingService:
    """ID映射服务测试"""

    def setup_method(self):
        """测试前准备"""
        self.service = IDMappingService()

    def test_generate_user_fingerprint(self):
        """测试用户指纹生成"""
        identifiers = {"phone": "13800138000", "email": "test@example.com"}
        fingerprint = self.service.generate_user_fingerprint(identifiers)

        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 16  # 应该是16位

    def test_fingerprint_consistency(self):
        """测试指纹一致性"""
        identifiers = {"phone": "13800138000"}
        fp1 = self.service.generate_user_fingerprint(identifiers)
        fp2 = self.service.generate_user_fingerprint(identifiers)

        assert fp1 == fp2

    def test_fingerprint_different_identifiers(self):
        """测试不同标识符产生不同指纹"""
        fp1 = self.service.generate_user_fingerprint({"phone": "13800138000"})
        fp2 = self.service.generate_user_fingerprint({"phone": "13900139000"})

        assert fp1 != fp2

    def test_map_identifiers(self):
        """测试标识映射"""
        unified_id = self.service.map_identifiers(
            user_id="user_001",
            platform="wechat",
            identifier_type="openid",
            identifier_value="oXXXXX"
        )

        assert unified_id is not None
        assert isinstance(unified_id, str)

    def test_get_unified_id_by_phone(self):
        """测试通过手机号获取统一ID"""
        unified_id = self.service.get_unified_id(phone="13800138000")

        assert unified_id is not None
        assert isinstance(unified_id, str)

    def test_get_unified_id_by_email(self):
        """测试通过邮箱获取统一ID"""
        unified_id = self.service.get_unified_id(email="test@example.com")

        assert unified_id is not None

    def test_get_unified_id_no_identifier(self):
        """测试无标识符时返回None"""
        unified_id = self.service.get_unified_id()

        assert unified_id is None


class TestAttributionService:
    """归因服务测试"""

    def setup_method(self):
        """测试前准备"""
        self.service = AttributionService()
        self.now = datetime.now()

    def test_calculate_attribution_first_touch(self):
        """测试首次触点归因计算"""
        events = self._create_mock_events()
        result = self.service.calculate_attribution(events, "first_touch")

        assert isinstance(result, dict)

    def test_calculate_attribution_last_touch(self):
        """测试末次触点归因计算"""
        events = self._create_mock_events()
        result = self.service.calculate_attribution(events, "last_touch")

        assert isinstance(result, dict)

    def test_calculate_attribution_unsupported_model(self):
        """测试不支持的归因模型"""
        events = self._create_mock_events()

        with pytest.raises(ValueError):
            self.service.calculate_attribution(events, "unsupported_model")

    def test_track_event(self):
        """测试事件追踪"""
        event = self.service.track_event(
            tenant_id="t1",
            event_type="citation",
            user_identifier="user_001",
            channel="deepseek",
            properties={"keyword": "品牌A"}
        )

        assert event.tenant_id == "t1"
        assert event.event_type == "citation"
        assert event.channel == "deepseek"
        assert event.event_time is not None

    def test_build_attribution_links(self):
        """测试构建归因链路"""
        events = self._create_mock_events()
        links = self.service.build_attribution_links(events, conversion_threshold=50)

        assert isinstance(links, list)

    def _create_mock_events(self):
        """创建模拟事件"""
        events = []
        channels = ["deepseek", "kimi", "wechat"]

        for i in range(10):
            event = AttributionEvent(
                tenant_id="t1",
                user_identifier=f"user_{i % 3}",
                event_type="conversion" if i % 4 == 0 else "citation",
                channel=channels[i % 3],
                event_time=self.now - timedelta(hours=10 - i),
                properties={"conversion_value": 100 if i % 4 == 0 else 0}
            )
            events.append(event)

        return events


class TestAttributionConversionValue:
    """归因转化价值测试"""

    def setup_method(self):
        """测试前准备"""
        self.service = AttributionService()

    def test_conversion_value_extraction(self):
        """测试转化价值提取"""
        event = AttributionEvent(
            tenant_id="t1",
            user_identifier="user_1",
            event_type="conversion",
            channel="deepseek",
            event_time=datetime.now(),
            properties={"conversion_value": 250}
        )

        assert self.service._get_conversion_value(event.properties) == 250

    def test_conversion_value_default(self):
        """测试默认转化价值"""
        event = AttributionEvent(
            tenant_id="t1",
            user_identifier="user_1",
            event_type="citation",
            channel="deepseek",
            event_time=datetime.now(),
            properties={}
        )

        assert self.service._get_conversion_value(event.properties) == 0
