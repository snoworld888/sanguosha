"""
GEO 智能优化平台 - ROI归因分析服务
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib

from src.models.schemas import (
    AttributionEvent,
    AttributionLink,
    AttributionReport
)


class AttributionModel:
    """归因模型"""

    def first_touch(self, events: List[AttributionEvent]) -> Dict[str, float]:
        """首次触点归因 - 100%归因于首次接触渠道"""
        if not events:
            return {}

        # 按用户分组
        user_events = defaultdict(list)
        for event in events:
            user_events[event.user_identifier].append(event)

        channel_weights = defaultdict(float)

        for user_id, user_event_list in user_events.items():
            # 找到首次触点
            first_event = min(user_event_list, key=lambda e: e.event_time)
            channel_weights[first_event.channel] += self._get_conversion_value(
                first_event.properties
            )

        return dict(channel_weights)

    def last_touch(self, events: List[AttributionEvent]) -> Dict[str, float]:
        """末次触点归因 - 100%归因于最后一次接触渠道"""
        if not events:
            return {}

        user_events = defaultdict(list)
        for event in events:
            user_events[event.user_identifier].append(event)

        channel_weights = defaultdict(float)

        for user_id, user_event_list in user_events.items():
            last_event = max(user_event_list, key=lambda e: e.event_time)
            channel_weights[last_event.channel] += self._get_conversion_value(
                last_event.properties
            )

        return dict(channel_weights)

    def linear(self, events: List[AttributionEvent]) -> Dict[str, float]:
        """线性归因 - 平均分配权重"""
        if not events:
            return {}

        user_events = defaultdict(list)
        for event in events:
            user_events[event.user_identifier].append(event)

        channel_weights = defaultdict(float)

        for user_id, user_event_list in user_events.items():
            weight_per_touchpoint = 1.0 / len(user_event_list)
            for event in user_event_list:
                channel_weights[event.channel] += (
                    self._get_conversion_value(event.properties) * weight_per_touchpoint
                )

        return dict(channel_weights)

    def time_decay(self, events: List[AttributionEvent], half_life_hours: int = 24) -> Dict[str, float]:
        """时间衰减归因 - 越接近转化权重越高"""
        if not events:
            return {}

        user_events = defaultdict(list)
        for event in events:
            user_events[event.user_identifier].append(event)

        channel_weights = defaultdict(float)

        for user_id, user_event_list in user_events.items():
            # 找到最后一次事件时间
            last_time = max(e.event_time for e in user_event_list)

            for event in user_event_list:
                # 计算时间衰减权重
                hours_diff = (last_time - event.event_time).total_seconds() / 3600
                decay_factor = 0.5 ** (hours_diff / half_life_hours)

                channel_weights[event.channel] += (
                    self._get_conversion_value(event.properties) * decay_factor
                )

        return dict(channel_weights)

    def custom(self, events: List[AttributionEvent], weights: Dict[str, float]) -> Dict[str, float]:
        """自定义归因 - 根据指定权重分配"""
        if not events:
            return {}

        channel_weights = defaultdict(float)

        for event in events:
            weight = weights.get(event.channel, 0)
            channel_weights[event.channel] += (
                self._get_conversion_value(event.properties) * weight
            )

        return dict(channel_weights)

    def _get_conversion_value(self, properties: Dict[str, Any]) -> float:
        """获取转化价值"""
        return properties.get("conversion_value", 1.0)


class IDMappingService:
    """跨平台ID-Mapping服务"""

    def __init__(self):
        # 简化实现，实际需要Redis存储映射关系
        self.mapping_cache: Dict[str, Dict[str, str]] = {}

    def generate_user_fingerprint(self, identifiers: Dict[str, str]) -> str:
        """生成用户指纹"""
        # 组合多个标识符生成唯一指纹
        combined = "|".join(f"{k}={v}" for k, v in sorted(identifiers.items()) if v)
        return hashlib.sha256(combined.encode()).hexdigest()[:16]

    def map_identifiers(
        self,
        user_id: str,
        platform: str,
        identifier_type: str,
        identifier_value: str
    ) -> str:
        """映射用户标识"""
        cache_key = f"{user_id}:{platform}:{identifier_type}"

        if cache_key not in self.mapping_cache:
            self.mapping_cache[cache_key] = {
                "user_id": user_id,
                "platform": platform,
                "identifier_type": identifier_type,
                "identifier_value": identifier_value,
                "unified_id": self.generate_user_fingerprint({
                    "user_id": user_id,
                    "platform": platform,
                    "id_type": identifier_type
                })
            }

        return self.mapping_cache[cache_key]["unified_id"]

    def get_unified_id(self, phone: str = None, email: str = None) -> Optional[str]:
        """通过手机号或邮箱获取统一ID"""
        if phone:
            return self.generate_user_fingerprint({"phone": phone})
        if email:
            return self.generate_user_fingerprint({"email": email})
        return None


class AttributionService:
    """归因分析服务"""

    def __init__(self):
        self.model = AttributionModel()
        self.id_mapping = IDMappingService()

    def calculate_attribution(
        self,
        events: List[AttributionEvent],
        model_type: str = "last_touch"
    ) -> Dict[str, float]:
        """计算归因"""
        if model_type == "first_touch":
            return self.model.first_touch(events)
        elif model_type == "last_touch":
            return self.model.last_touch(events)
        elif model_type == "linear":
            return self.model.linear(events)
        elif model_type == "time_decay":
            return self.model.time_decay(events)
        else:
            raise ValueError(f"不支持的归因模型: {model_type}")

    def build_attribution_links(
        self,
        events: List[AttributionEvent],
        conversion_threshold: float = 0.0
    ) -> List[AttributionLink]:
        """构建归因链路"""
        if not events:
            return []

        # 按用户分组
        user_events = defaultdict(list)
        for event in events:
            user_events[event.user_identifier].append(event)

        links = []

        for user_id, user_event_list in user_events.items():
            # 按时间排序
            sorted_events = sorted(user_event_list, key=lambda e: e.event_time)

            # 检查是否达到转化阈值
            total_value = sum(
                self._get_conversion_value(e.properties)
                for e in sorted_events
            )

            if total_value >= conversion_threshold:
                link = AttributionLink(
                    events=sorted_events,
                    total_touchpoints=len(sorted_events),
                    attributed_conversion_value=total_value,
                    attribution_model="multi_touch"
                )
                links.append(link)

        return links

    def generate_report(
        self,
        tenant_id: str,
        events: List[AttributionEvent],
        date_range: Dict[str, datetime],
        model_type: str = "last_touch"
    ) -> AttributionReport:
        """生成归因报告"""
        # 计算各渠道归因
        channel_weights = self.calculate_attribution(events, model_type)

        # 找出转化事件
        conversion_events = [
            e for e in events
            if e.event_type in ["purchase", "signup", "conversion"]
        ]

        # 统计总引用数和转化数
        ai_citation_events = [
            e for e in events
            if e.channel in ["deepseek", "kimi", "doubao", "wenxin", "tongyi"]
        ]

        total_citations = len(ai_citation_events)
        total_conversions = len(conversion_events)
        conversion_rate = (
            total_conversions / total_citations if total_citations > 0 else 0
        )

        # 计算ROI
        total_cost = sum(
            e.properties.get("cost", 0)
            for e in events
        )
        total_revenue = sum(
            self._get_conversion_value(e.properties)
            for e in conversion_events
        )
        roi = (total_revenue - total_cost) / total_cost if total_cost > 0 else 0

        # Top渠道
        top_channels = sorted(
            channel_weights.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        top_channels_data = [
            {"channel": ch, "value": round(val, 2), "percentage": round(val / sum(channel_weights.values()) * 100, 2)}
            for ch, val in top_channels
        ]

        # 构建归因链路
        attribution_links = self.build_attribution_links(events)

        return AttributionReport(
            id=str(tenant_id),
            tenant_id=tenant_id,
            date_range={
                "start": date_range.get("start", datetime.now() - timedelta(days=30)),
                "end": date_range.get("end", datetime.now())
            },
            total_citations=total_citations,
            total_conversions=total_conversions,
            conversion_rate=round(conversion_rate, 4),
            roi=round(roi, 2),
            top_channels=top_channels_data,
            attribution_links=attribution_links,
            created_at=datetime.now()
        )

    def track_event(
        self,
        tenant_id: str,
        event_type: str,
        user_identifier: str,
        channel: str,
        properties: Dict[str, Any] = None,
        campaign: str = None
    ) -> AttributionEvent:
        """追踪事件"""
        event = AttributionEvent(
            tenant_id=tenant_id,
            user_identifier=user_identifier,
            event_type=event_type,
            channel=channel,
            campaign=campaign,
            event_time=datetime.now(),
            properties=properties or {}
        )

        # 如果是转化事件，进行ID映射
        if event_type in ["purchase", "signup", "conversion"]:
            # 简化实现，实际需要存储到数据库
            pass

        return event

    def _get_conversion_value(self, properties: Dict[str, Any]) -> float:
        """获取转化价值"""
        return properties.get("conversion_value", 0.0)


# 服务单例
attribution_service = AttributionService()
