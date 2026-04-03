"""
GEO 智能优化平台 - 关键词管理路由
"""
from typing import List
from fastapi import APIRouter, HTTPException, status, Depends, Query

from src.core.security import get_current_user
from src.models.schemas import Keyword, KeywordCreate, PaginatedResponse

router = APIRouter()


# 模拟数据存储
_mock_keywords = {}


@router.get("/", response_model=List[Keyword])
async def list_keywords(
    page: int = 1,
    page_size: int = 20,
    platform: str = None,
    is_active: bool = None,
    current_user: dict = Depends(get_current_user)
):
    """
    获取关键词列表

    - **page**: 页码
    - **page_size**: 每页数量
    - **platform**: 筛选平台
    - **is_active**: 筛选激活状态
    """
    keywords = list(_mock_keywords.values())

    if platform:
        keywords = [k for k in keywords if platform in k.platforms]
    if is_active is not None:
        keywords = [k for k in keywords if k.is_active == is_active]

    return keywords[(page - 1) * page_size: page * page_size]


@router.get("/{keyword_id}", response_model=Keyword)
async def get_keyword(
    keyword_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    获取关键词详情

    - **keyword_id**: 关键词ID
    """
    if keyword_id not in _mock_keywords:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="关键词不存在"
        )
    return _mock_keywords[keyword_id]


@router.post("/", response_model=Keyword, status_code=status.HTTP_201_CREATED)
async def create_keyword(
    keyword: KeywordCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    创建关键词

    - **brand_name**: 品牌名称
    - **synonyms**: 同义词列表
    - **competitors**: 竞品列表
    - **platforms**: 监测平台列表
    - **frequency**: 监测频率
    """
    from datetime import datetime
    import uuid

    new_keyword = Keyword(
        id=str(uuid.uuid4()),
        tenant_id=keyword.tenant_id,
        brand_name=keyword.brand_name,
        synonyms=keyword.synonyms,
        competitors=keyword.competitors,
        platforms=[p.value for p in keyword.platforms],
        frequency=keyword.frequency.value,
        is_active=True,
        created_at=datetime.now()
    )
    _mock_keywords[new_keyword.id] = new_keyword
    return new_keyword


@router.put("/{keyword_id}", response_model=Keyword)
async def update_keyword(
    keyword_id: str,
    keyword: KeywordCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    更新关键词

    - **keyword_id**: 关键词ID
    """
    if keyword_id not in _mock_keywords:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="关键词不存在"
        )

    existing = _mock_keywords[keyword_id]
    existing.brand_name = keyword.brand_name
    existing.synonyms = keyword.synonyms
    existing.competitors = keyword.competitors
    existing.platforms = [p.value for p in keyword.platforms]
    existing.frequency = keyword.frequency.value

    return existing


@router.delete("/{keyword_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_keyword(
    keyword_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    删除关键词（软删除）

    - **keyword_id**: 关键词ID
    """
    if keyword_id in _mock_keywords:
        _mock_keywords[keyword_id].is_active = False
