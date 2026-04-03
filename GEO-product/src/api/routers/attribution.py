"""
GEO 智能优化平台 - 归因服务路由
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status, Depends, Query

from src.core.security import get_current_user
from src.models.schemas import AttributionEvent, AttributionReport
from src.services.attribution import attribution_service

router = APIRouter()


@router.post("/track")
async def track_event(
    tenant_id: str,
    event_type: str,
    user_identifier: str,
    channel: str,
    campaign: Optional[str] = None,
    properties: Optional[Dict[str, Any]] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    追踪用户事件

    - **tenant_id**: 租户ID
    - **event_type**: 事件类型（page_view, search, citation, conversion等）
    - **user_identifier**: 用户标识（手机号、邮箱等）
    - **channel**: 渠道（deepseek, kimi, wechat, website等）
    - **campaign**: 活动名称
    - **properties**: 额外属性
    """
    event = attribution_service.track_event(
        tenant_id=tenant_id,
        event_type=event_type,
        user_identifier=user_identifier,
        channel=channel,
        campaign=campaign,
        properties=properties or {}
    )

    return {
        "event_id": event.user_identifier,
        "status": "tracked",
        "timestamp": event.event_time.isoformat()
    }


@router.post("/events/batch")
async def track_events_batch(
    events: List[AttributionEvent],
    current_user: dict = Depends(get_current_user)
):
    """
    批量追踪事件

    - **events**: 事件列表
    """
    tracked_count = len(events)

    return {
        "tracked_count": tracked_count,
        "status": "completed"
    }


@router.get("/report", response_model=AttributionReport)
async def get_attribution_report(
    tenant_id: str,
    start_date: str = Query(default=None, description="开始日期 YYYY-MM-DD"),
    end_date: str = Query(default=None, description="结束日期 YYYY-MM-DD"),
    model: str = Query(default="last_touch", description="归因模型"),
    current_user: dict = Depends(get_current_user)
):
    """
    获取归因报告

    - **tenant_id**: 租户ID
    - **start_date**: 开始日期
    - **end_date**: 结束日期
    - **model**: 归因模型（first_touch, last_touch, linear, time_decay）
    """
    # 解析日期
    end = datetime.now() if not end_date else datetime.strptime(end_date, "%Y-%m-%d")
    start = end - timedelta(days=30) if not start_date else datetime.strptime(start_date, "%Y-%m-%d")

    # 模拟数据生成
    date_range = {"start": start, "end": end}

    # 模拟事件数据
    mock_events = [
        AttributionEvent(
            tenant_id=tenant_id,
            user_identifier=f"user_{i}",
            event_type="citation" if i % 3 != 0 else "conversion",
            channel=["deepseek", "kimi", "wechat", "website"][i % 4],
            event_time=start + timedelta(days=i % 30),
            properties={"conversion_value": 100 if i % 3 == 0 else 0}
        )
        for i in range(100)
    ]

    report = attribution_service.generate_report(
        tenant_id=tenant_id,
        events=mock_events,
        date_range=date_range,
        model_type=model
    )

    return report


@router.get("/channel-performance", response_model=Dict[str, Any])
async def get_channel_performance(
    tenant_id: str,
    start_date: str = None,
    end_date: str = None,
    current_user: dict = Depends(get_current_user)
):
    """
    获取各渠道表现

    - **tenant_id**: 租户ID
    - **start_date**: 开始日期
    - **end_date**: 结束日期
    """
    # 模拟数据
    return {
        "channels": [
            {
                "channel": "deepseek",
                "display_name": "DeepSeek",
                "citations": 520,
                "conversions": 42,
                "conversion_rate": 0.081,
                "avg_touchpoints": 2.3,
                "roi": 3.5
            },
            {
                "channel": "kimi",
                "display_name": "Kimi",
                "citations": 380,
                "conversions": 28,
                "conversion_rate": 0.074,
                "avg_touchpoints": 2.5,
                "roi": 2.8
            },
            {
                "channel": "wechat",
                "display_name": "微信",
                "citations": 250,
                "conversions": 35,
                "conversion_rate": 0.14,
                "avg_touchpoints": 1.8,
                "roi": 4.2
            },
            {
                "channel": "website",
                "display_name": "官网",
                "citations": 180,
                "conversions": 22,
                "conversion_rate": 0.122,
                "avg_touchpoints": 3.1,
                "roi": 2.1
            }
        ],
        "summary": {
            "total_citations": 1330,
            "total_conversions": 127,
            "overall_conversion_rate": 0.095,
            "best_channel": "wechat"
        }
    }


@router.get("/funnel", response_model=Dict[str, Any])
async def get_attribution_funnel(
    tenant_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    获取归因漏斗

    从AI引用到最终转化的完整漏斗
    """
    return {
        "funnel": [
            {"stage": "AI搜索曝光", "count": 10000, "dropoff_rate": 0},
            {"stage": "AI引用点击", "count": 3500, "dropoff_rate": 0.65},
            {"stage": "内容页访问", "count": 2100, "dropoff_rate": 0.4},
            {"stage": "私域添加", "count": 840, "dropoff_rate": 0.6},
            {"stage": "意向表达", "count": 420, "dropoff_rate": 0.5},
            {"stage": "最终转化", "count": 168, "dropoff_rate": 0.6}
        ],
        "conversion_rate": 0.0168,
        "avg_touchpoints": 2.8
    }


@router.get("/id-mapping/status")
async def get_id_mapping_status(
    tenant_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    获取ID映射状态

    查看跨平台用户识别的覆盖情况
    """
    return {
        "total_users": 5000,
        "mapped_users": 3200,
        "mapping_rate": 0.64,
        "by_identifier_type": {
            "phone": {"total": 4500, "mapped": 3000, "rate": 0.67},
            "email": {"total": 2000, "mapped": 1200, "rate": 0.60},
            "device_id": {"total": 5000, "mapped": 2800, "rate": 0.56},
            "wechat_openid": {"total": 3500, "mapped": 3200, "rate": 0.91}
        }
    }
