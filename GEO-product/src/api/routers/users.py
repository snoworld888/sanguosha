"""
GEO 智能优化平台 - 用户管理路由
"""
from typing import List
from fastapi import APIRouter, HTTPException, status, Depends

from src.core.security import get_current_user
from src.models.schemas import User, UserCreate, PaginatedResponse

router = APIRouter()


# 模拟数据存储
_mock_users = {}


@router.get("/", response_model=List[User])
async def list_users(
    page: int = 1,
    page_size: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """
    获取用户列表

    - **page**: 页码
    - **page_size**: 每页数量
    """
    return list(_mock_users.values())[(page - 1) * page_size: page * page_size]


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    获取用户详情

    - **user_id**: 用户ID
    """
    if user_id not in _mock_users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return _mock_users[user_id]


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    创建用户

    - **email**: 用户邮箱
    - **username**: 用户名
    - **password**: 密码
    - **tenant_id**: 租户ID
    - **role**: 角色
    """
    from datetime import datetime
    import uuid
    from src.core.security import get_password_hash

    new_user = User(
        id=str(uuid.uuid4()),
        email=user.email,
        username=user.username,
        role=user.role,
        tenant_id=user.tenant_id,
        is_active=True,
        created_at=datetime.now()
    )
    _mock_users[new_user.id] = new_user
    return new_user


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    user: UserCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    更新用户

    - **user_id**: 用户ID
    """
    if user_id not in _mock_users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    existing = _mock_users[user_id]
    existing.email = user.email
    existing.username = user.username
    existing.role = user.role

    return existing


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    删除用户

    - **user_id**: 用户ID
    """
    if user_id in _mock_users:
        del _mock_users[user_id]
