"""
GEO 智能优化平台 - 内容管理路由
"""
from typing import List
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from fastapi.responses import StreamingResponse
import io

from src.core.security import get_current_user
from src.models.schemas import (
    ContentSource,
    ContentSourceCreate,
    ContentGenerationRequest,
    ContentGenerationResponse,
    PaginatedResponse
)
from src.services.content import content_generation_service

router = APIRouter()


# 模拟数据存储
_mock_contents = {}


@router.get("/", response_model=List[ContentSource])
async def list_contents(
    page: int = 1,
    page_size: int = 20,
    platform: str = None,
    content_type: str = None,
    current_user: dict = Depends(get_current_user)
):
    """
    获取内容列表

    - **page**: 页码
    - **page_size**: 每页数量
    - **platform**: 筛选平台
    - **content_type**: 筛选内容类型
    """
    contents = list(_mock_contents.values())

    if platform:
        contents = [c for c in contents if c.platform == platform]
    if content_type:
        contents = [c for c in contents if c.content_type == content_type]

    return contents[(page - 1) * page_size: page * page_size]


@router.get("/{content_id}", response_model=ContentSource)
async def get_content(
    content_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    获取内容详情

    - **content_id**: 内容ID
    """
    if content_id not in _mock_contents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="内容不存在"
        )
    return _mock_contents[content_id]


@router.post("/", response_model=ContentSource, status_code=status.HTTP_201_CREATED)
async def create_content(
    content: ContentSourceCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    创建内容记录

    - **platform**: 平台
    - **content_type**: 内容类型
    - **title**: 标题
    - **url**: 原文链接
    - **author**: 作者
    """
    from datetime import datetime
    import uuid

    new_content = ContentSource(
        id=str(uuid.uuid4()),
        tenant_id=content.tenant_id,
        platform=content.platform.value,
        content_type=content.content_type.value,
        title=content.title,
        summary=content.summary,
        url=content.url,
        author=content.author,
        author_id=content.author_id,
        content_id=content.content_id,
        publish_time=content.publish_time,
        metrics=content.metrics.model_dump(),
        geo_tags=[],
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    _mock_contents[new_content.id] = new_content
    return new_content


@router.post("/generate", response_model=ContentGenerationResponse)
async def generate_content(
    request: ContentGenerationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    生成GEO优化内容

    - **platform**: 目标平台
    - **content_type**: 内容类型
    - **topic**: 主题
    - **keywords**: 关键词列表
    - **tone**: 语气风格
    - **length**: 目标长度
    """
    return await content_generation_service.generate_content(request)


@router.post("/upload")
async def upload_content(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    上传内容文件进行GEO分析

    支持格式: txt, md, docx, pdf
    """
    content = await file.read()

    # 简化实现，实际需要解析文件内容
    return {
        "filename": file.filename,
        "size": len(content),
        "status": "uploaded",
        "message": "文件上传成功，开始分析..."
    }


@router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content(
    content_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    删除内容记录

    - **content_id**: 内容ID
    """
    if content_id in _mock_contents:
        del _mock_contents[content_id]
