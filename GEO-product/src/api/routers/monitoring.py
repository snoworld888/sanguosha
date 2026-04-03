"""
GEO 智能优化平台 - 监测服务路由
"""
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks

from src.core.security import get_current_user
from src.models.schemas import (
    PlatformEnum,
    MonitoringTaskCreate,
    MonitoringTask,
    CitationRecord,
    CitationRecordCreate
)
from src.services.monitoring import monitoring_service

router = APIRouter()


# 模拟数据存储
_mock_tasks = {}
_mock_citations = {}


@router.get("/platforms", response_model=List[Dict[str, Any]])
async def list_platforms():
    """
    获取支持的AI平台列表
    """
    platforms = [
        {"id": "deepseek", "name": "DeepSeek", "status": "active", "priority": 0},
        {"id": "kimi", "name": "Kimi", "status": "active", "priority": 0},
        {"id": "doubao", "name": "豆包", "status": "active", "priority": 1},
        {"id": "wenxin", "name": "文心一言", "status": "active", "priority": 0},
        {"id": "tongyi", "name": "通义千问", "status": "active", "priority": 0},
        {"id": "yuanbao", "name": "腾讯元宝", "status": "active", "priority": 1},
        {"id": "chatgpt", "name": "ChatGPT", "status": "inactive", "priority": 2},
        {"id": "gemini", "name": "Gemini", "status": "inactive", "priority": 2},
        {"id": "claude", "name": "Claude", "status": "inactive", "priority": 2},
    ]
    return platforms


@router.get("/tasks", response_model=List[MonitoringTask])
async def list_tasks(
    page: int = 1,
    page_size: int = 20,
    status: str = None,
    current_user: dict = Depends(get_current_user)
):
    """
    获取监测任务列表
    """
    tasks = list(_mock_tasks.values())

    if status:
        tasks = [t for t in tasks if t.status == status]

    return tasks[(page - 1) * page_size: page * page_size]


@router.get("/tasks/{task_id}", response_model=MonitoringTask)
async def get_task(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    获取监测任务详情
    """
    if task_id not in _mock_tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    return _mock_tasks[task_id]


@router.post("/tasks", response_model=MonitoringTask, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: MonitoringTaskCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    创建监测任务

    - **name**: 任务名称
    - **keywords**: 关键词列表
    - **platforms**: 监测平台列表
    - **frequency**: 监测频率
    """
    from datetime import datetime
    import uuid

    next_run = monitoring_service.calculate_next_run_time(task.frequency)

    new_task = MonitoringTask(
        id=str(uuid.uuid4()),
        tenant_id=task.tenant_id,
        name=task.name,
        keywords=task.keywords,
        platforms=[p.value for p in task.platforms],
        frequency=task.frequency.value,
        status="pending",
        next_run_at=next_run,
        created_at=datetime.now()
    )
    _mock_tasks[new_task.id] = new_task
    return new_task


@router.post("/tasks/{task_id}/run")
async def run_task(
    task_id: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    手动触发监测任务

    - **task_id**: 任务ID
    """
    if task_id not in _mock_tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )

    task = _mock_tasks[task_id]
    task.status = "running"

    # 在后台执行（简化实现）
    return {
        "message": "任务已开始执行",
        "task_id": task_id,
        "status": "running"
    }


@router.get("/citations", response_model=List[CitationRecord])
async def list_citations(
    page: int = 1,
    page_size: int = 20,
    platform: str = None,
    keyword: str = None,
    start_date: str = None,
    end_date: str = None,
    current_user: dict = Depends(get_current_user)
):
    """
    获取引用记录列表

    - **platform**: 筛选平台
    - **keyword**: 筛选关键词
    - **start_date**: 开始日期
    - **end_date**: 结束日期
    """
    citations = list(_mock_citations.values())

    if platform:
        citations = [c for c in citations if c.ai_platform == platform]
    if keyword:
        citations = [c for c in citations if keyword in c.brand_keyword]

    return citations[(page - 1) * page_size: page * page_size]


@router.post("/batch", response_model=Dict[str, Any])
async def batch_monitor(
    tenant_id: str,
    keywords: List[str],
    platforms: List[PlatformEnum],
    frequency: str = "daily",
    current_user: dict = Depends(get_current_user)
):
    """
    批量执行监测

    - **tenant_id**: 租户ID
    - **keywords**: 关键词列表
    - **platforms**: 监测平台列表
    - **frequency**: 监测频率
    """
    result = await monitoring_service.batch_monitor(
        tenant_id=tenant_id,
        keywords=keywords,
        platforms=platforms
    )
    return result
