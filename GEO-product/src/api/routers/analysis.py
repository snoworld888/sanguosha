"""
GEO 智能优化平台 - 分析服务路由
"""
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends

from src.core.security import get_current_user
from src.models.schemas import (
    GEMScore,
    DiagnosisReport,
    AnalysisReport,
    ContentSource
)
from src.services.analysis import analysis_service

router = APIRouter()


@router.post("/gem-score", response_model=GEMScore)
async def calculate_gem_score(
    content: str,
    metadata: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """
    计算GEM评分

    - **content**: 内容文本
    - **metadata**: 元数据（平台、作者、粉丝数等）
    """
    score = analysis_service.calculate_gem_score(content, metadata)
    return score


@router.post("/diagnosis", response_model=DiagnosisReport)
async def generate_diagnosis(
    content: str,
    metadata: Dict[str, Any],
    competitors: List[Dict[str, Any]] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    生成优化诊断报告

    - **content**: 内容文本
    - **metadata**: 元数据
    - **competitors**: 竞品信息（可选）
    """
    diagnosis = analysis_service.generate_diagnosis(content, metadata, competitors)
    return diagnosis


@router.post("/full-report", response_model=Dict[str, Any])
async def generate_full_report(
    content: str,
    metadata: Dict[str, Any],
    competitors: List[Dict[str, Any]] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    生成完整分析报告

    包含GEM评分和优化诊断
    """
    gem_score = analysis_service.calculate_gem_score(content, metadata)
    diagnosis = analysis_service.generate_diagnosis(content, metadata, competitors)

    return {
        "gem_score": gem_score.model_dump(),
        "diagnosis": diagnosis.model_dump(),
        "summary": {
            "overall_score": gem_score.total,
            "key_issues": diagnosis.content_gaps[:3],
            "top_suggestions": diagnosis.structure_suggestions[:3]
        }
    }


@router.get("/trends", response_model=Dict[str, Any])
async def get_citation_trends(
    tenant_id: str,
    start_date: str = None,
    end_date: str = None,
    current_user: dict = Depends(get_current_user)
):
    """
    获取引用趋势分析

    - **tenant_id**: 租户ID
    - **start_date**: 开始日期
    - **end_date**: 结束日期
    """
    # 模拟数据
    return {
        "has_data": True,
        "trend": "increasing",
        "total_citations": 1250,
        "daily_average": 41.67,
        "peak_date": "2026-03-20",
        "daily_counts": {
            "2026-03-18": 35,
            "2026-03-19": 42,
            "2026-03-20": 58,
            "2026-03-21": 45,
            "2026-03-22": 38,
            "2026-03-23": 32
        },
        "by_platform": {
            "deepseek": 520,
            "kimi": 380,
            "doubao": 250,
            "wenxin": 100
        },
        "by_keyword": {
            "品牌A": 450,
            "品牌B": 380,
            "产品X": 280,
            "产品Y": 140
        }
    }


@router.get("/competitor-analysis", response_model=Dict[str, Any])
async def competitor_analysis(
    tenant_id: str,
    keyword: str,
    current_user: dict = Depends(get_current_user)
):
    """
    竞品引用分析

    - **tenant_id**: 租户ID
    - **keyword**: 关键词
    """
    # 模拟数据
    return {
        "keyword": keyword,
        "your_citations": 320,
        "competitors": [
            {
                "name": "竞品A",
                "citations": 580,
                "market_share": 45.2,
                "trending": "increasing"
            },
            {
                "name": "竞品B",
                "citations": 280,
                "market_share": 21.8,
                "trending": "stable"
            },
            {
                "name": "竞品C",
                "citations": 120,
                "market_share": 9.4,
                "trending": "decreasing"
            }
        ],
        "market_opportunity": "在'品牌对比'类问题中，你的品牌被引用率较低，建议加强对比类内容输出"
    }


@router.get("/content-gaps", response_model=Dict[str, Any])
async def analyze_content_gaps(
    tenant_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    内容缺口分析

    识别高价值问题未覆盖的内容领域
    """
    # 模拟数据
    return {
        "high_value_gaps": [
            {
                "topic": "XXX品牌 vs YYY品牌",
                "search_volume": "高",
                "ai_citation_rate": 0.72,
                "difficulty": "中",
                "suggestion": "建议发布对比评测文章"
            },
            {
                "topic": "XXX产品使用教程",
                "search_volume": "高",
                "ai_citation_rate": 0.65,
                "difficulty": "低",
                "suggestion": "建议制作视频教程"
            },
            {
                "topic": "XXX行业趋势分析",
                "search_volume": "中",
                "ai_citation_rate": 0.58,
                "difficulty": "高",
                "suggestion": "建议联合行业专家发布"
            }
        ],
        "questions_to_answer": [
            "XXX品牌真的好用吗？",
            "XXX和YYY哪个性价比高？",
            "XXX怎么使用最有效？"
        ]
    }
