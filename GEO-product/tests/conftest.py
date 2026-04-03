"""
GEO 智能优化平台 - pytest配置文件
"""
import sys
from pathlib import Path

# 添加src到Python路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

import pytest


@pytest.fixture(scope="session")
def anyio_backend():
    """配置异步后端"""
    return "asyncio"


@pytest.fixture
def sample_content():
    """示例内容"""
    return """
    # GEO产品深度评测

    作为一个专业的GEO优化平台，我们对该产品进行了全面评测。

    ## 产品概述

    GEO（Generative Engine Optimization）是生成式引擎优化的缩写，
    这是一个新兴的营销领域，帮助品牌在AI搜索时代获得更好的曝光。

    ## 核心功能

    1. AI平台监测：支持DeepSeek、Kimi、豆包等9+平台
    2. 内容分析：基于GEM评分模型进行效果评估
    3. 智能生成：自动生成GEO优化内容
    4. ROI归因：全链路转化追踪

    ## 性能数据

    数据显示，使用GEO优化后，品牌的AI引用率平均提升3倍。

    ## 总结

    总体来说，这是一款值得关注的产品。
    """


@pytest.fixture
def sample_metadata():
    """示例元数据"""
    return {
        "platform": "wechat",
        "is_verified": True,
        "followers": 25000,
        "author": "张三",
        "has_images": True
    }


@pytest.fixture
def sample_competitors():
    """示例竞品数据"""
    return [
        {"name": "灵通GEO", "cited_topics": ["功能全面", "价格高"], "citations": 580},
        {"name": "SheepGeo", "cited_topics": ["免费", "覆盖广"], "citations": 420},
        {"name": "优采云", "cited_topics": ["性价比", "自动化"], "citations": 280}
    ]


@pytest.fixture
def mock_tenant_id():
    """模拟租户ID"""
    return "test_tenant_001"


@pytest.fixture
def mock_user_id():
    """模拟用户ID"""
    return "test_user_001"
