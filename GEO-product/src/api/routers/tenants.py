"""
GEO 智能优化平台 - 租户管理路由
"""
from typing import List
from fastapi import APIRouter, HTTPException, status, Depends

from src.core.security import get_current_user
from src.models.schemas import Tenant, TenantCreate, PaginatedResponse

router = APIRouter()


# 模拟数据存储
_mock_tenants = {}


@router.get("/", response_model=List[Tenant])
async def list_tenants(
    page: int = 1,
    page_size: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """
    获取租户列表

    - **page**: 页码
    - **page_size**: 每页数量
    """
    # 实际从数据库查询
    return list(_mock_tenants.values())[(page - 1) * page_size: page * page_size]


@router.get("/{tenant_id}", response_model=Tenant)
async def get_tenant(
    tenant_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    获取租户详情

    - **tenant_id**: 租户ID
    """
    if tenant_id not in _mock_tenants:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="租户不存在"
        )
    return _mock_tenants[tenant_id]


@router.post("/", response_model=Tenant, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    tenant: TenantCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    创建租户

    - **name**: 租户名称
    - **plan**: 套餐类型
    - **contact_email**: 联系邮箱
    """
    from datetime import datetime
    import uuid

    new_tenant = Tenant(
        id=str(uuid.uuid4()),
        name=tenant.name,
        plan=tenant.plan,
        contact_email=tenant.contact_email,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    _mock_tenants[new_tenant.id] = new_tenant
    return new_tenant


@router.put("/{tenant_id}", response_model=Tenant)
async def update_tenant(
    tenant_id: str,
    tenant: TenantCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    更新租户

    - **tenant_id**: 租户ID
    """
    if tenant_id not in _mock_tenants:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="租户不存在"
        )

    from datetime import datetime
    existing = _mock_tenants[tenant_id]
    existing.name = tenant.name
    existing.plan = tenant.plan
    existing.contact_email = tenant.contact_email
    existing.updated_at = datetime.now()

    return existing


@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tenant(
    tenant_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    删除租户

    - **tenant_id**: 租户ID
    """
    if tenant_id in _mock_tenants:
        del _mock_tenants[tenant_id]
