"""API 安全模块 — Bearer Token 认证 + CORS 配置"""
import os

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

API_TOKEN = os.environ.get("API_TOKEN", "")
_security_scheme = HTTPBearer(auto_error=False)


def verify_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(_security_scheme),
) -> None:
    """依赖注入：验证 Bearer Token。API_TOKEN 为空时跳过认证（开发模式）。"""
    if not API_TOKEN:
        return
    if credentials is None or credentials.credentials != API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API token.",
        )


def add_security_middleware(app: FastAPI) -> None:
    """添加 CORS 中间件。"""
    origins = os.environ.get("CORS_ORIGINS", "*").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )
