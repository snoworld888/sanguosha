"""
GEO 智能优化平台 - 认证路由
"""
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from src.core.security import (
    verify_password,
    get_password_hash,
    create_access_token
)
from src.core.config import settings
from src.models.schemas import LoginRequest, TokenResponse

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    用户登录，获取访问令牌

    - **username**: 用户邮箱
    - **password**: 用户密码
    """
    # 简化实现，实际需要从数据库验证用户
    # 这里模拟一个用户验证过程
    if form_data.username == "admin@geo.com" and form_data.password == "admin123":
        access_token = create_access_token(
            data={
                "sub": "user_001",
                "tenant_id": "tenant_001",
                "role": "admin"
            },
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="邮箱或密码错误",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post("/login/json", response_model=TokenResponse)
async def login_json(credentials: LoginRequest):
    """
    JSON格式登录

    - **email**: 用户邮箱
    - **password**: 用户密码
    """
    if credentials.email == "admin@geo.com" and credentials.password == "admin123":
        access_token = create_access_token(
            data={
                "sub": "user_001",
                "tenant_id": "tenant_001",
                "role": "admin"
            },
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="邮箱或密码错误"
    )


@router.post("/refresh")
async def refresh_token():
    """
    刷新访问令牌

    注意：需要传入有效的refresh_token
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Token刷新功能开发中"
    )


@router.post("/logout")
async def logout():
    """
    用户登出

    注意：实际实现需要在服务端使token失效
    """
    return {"message": "登出成功"}
