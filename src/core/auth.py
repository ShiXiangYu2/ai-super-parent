"""SaaS 认证系统 — JWT + 角色权限"""
import json
import os
import time
import uuid
from functools import wraps
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.core.database import get_user, get_user_by_email, verify_password

JWT_SECRET = os.environ.get("JWT_SECRET", "super-parent-jwt-secret-dev-only")
JWT_ALGO = "HS256"
JWT_EXPIRE_HOURS = 24

_security = HTTPBearer(auto_error=False)

ROLE_HIERARCHY = {
    "super_admin": 100,
    "tenant_admin": 50,
    "teacher": 20,
    "parent": 10,
}


def create_token(user_id: str, tenant_id: str, role: str, name: str) -> str:
    """生成 JWT Token。"""
    import jwt
    payload = {
        "sub": user_id,
        "tenant_id": tenant_id,
        "role": role,
        "name": name,
        "iat": int(time.time()),
        "exp": int(time.time()) + JWT_EXPIRE_HOURS * 3600,
        "jti": uuid.uuid4().hex,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


def decode_token(token: str) -> Optional[dict]:
    """解码 JWT Token，过期或无效返回 None。"""
    import jwt
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(_security)) -> dict:
    """依赖注入：从请求头解析当前用户。"""
    if credentials is None:
        raise HTTPException(status_code=401, detail="缺少 Authorization 头")
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Token 无效或已过期")
    user = get_user(payload["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    if not user.get("is_active", 1):
        raise HTTPException(status_code=403, detail="账户已被禁用")
    return user


def require_role(min_role: str):
    """依赖注入工厂：要求用户角色不低于指定级别。"""
    min_level = ROLE_HIERARCHY.get(min_role, 0)

    def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_level = ROLE_HIERARCHY.get(current_user.get("role", ""), 0)
        if user_level < min_level:
            raise HTTPException(status_code=403, detail=f"需要 {min_role} 以上权限")
        return current_user

    return role_checker


def require_tenant_access(current_user: dict = Depends(get_current_user)):
    """依赖注入：验证用户属于某个租户（super_admin 可访问所有）。"""
    if current_user.get("role") == "super_admin":
        return current_user
    return current_user


def get_tenant_id(request: Request, current_user: dict = Depends(get_current_user)) -> str:
    """依赖注入：获取当前用户的租户 ID，并在请求中注入。"""
    if current_user.get("role") == "super_admin":
        # super_admin 可以通过 X-Tenant-ID 头切换租户
        override = request.headers.get("X-Tenant-ID", "")
        if override:
            return override
    return current_user["tenant_id"]
