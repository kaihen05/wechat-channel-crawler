from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter(prefix="/api/auth", tags=["认证"])

# 延迟导入避免循环依赖
def _get_settings():
    from app.config import settings
    return settings

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


class LoginRequest(BaseModel):
    password: str
    role: str = "viewer"  # "admin" 或 "viewer"


class TokenResponse(BaseModel):
    success: bool
    token: str
    message: str
    role: str


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建 JWT token"""
    settings = _get_settings()
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=ALGORITHM)


def verify_token(request: Request) -> bool:
    """验证请求中的 token，返回是否有效"""
    payload = get_token_payload(request)
    return payload is not None


def get_token_payload(request: Request) -> Optional[dict]:
    """解析并返回 token payload，无效返回 None"""
    settings = _get_settings()
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]

    if not token:
        return None

    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def is_admin(request: Request) -> bool:
    """检查当前用户是否为超级管理者"""
    payload = get_token_payload(request)
    if not payload:
        return False
    return payload.get("role") == "admin"


async def require_auth(request: Request):
    """依赖项：要求认证"""
    if not verify_token(request):
        raise HTTPException(status_code=401, detail="未登录或登录已过期")


async def require_admin(request: Request):
    """依赖项：要求超级管理者权限"""
    if not verify_token(request):
        raise HTTPException(status_code=401, detail="未登录或登录已过期")
    if not is_admin(request):
        raise HTTPException(status_code=403, detail="需要超级管理者权限")


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, response: Response):
    """密码登录 - 支持两种角色"""
    settings = _get_settings()
    role = request.role

    # 根据角色验证不同密码
    if role == "admin":
        if request.password != settings.admin_password:
            raise HTTPException(status_code=401, detail="管理者密码错误")
    else:
        # 普通用户可以用普通密码，也可以用管理者密码（自动升级为admin）
        if request.password == settings.admin_password:
            role = "admin"
        elif request.password != settings.access_password:
            raise HTTPException(status_code=401, detail="密码错误")

    token = create_access_token(data={"sub": "authenticated", "role": role})

    # 设置 cookie
    response = JSONResponse(content={
        "success": True,
        "token": token,
        "message": "登录成功",
        "role": role
    })
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_HOURS * 3600,
        samesite="lax",
    )
    return response


@router.post("/logout")
async def logout():
    """登出"""
    response = JSONResponse(content={"success": True, "message": "已登出"})
    response.delete_cookie(key="access_token")
    return response


@router.get("/status")
async def auth_status(request: Request):
    """检查登录状态，包含角色信息"""
    payload = get_token_payload(request)
    if payload:
        return {
            "authenticated": True,
            "role": payload.get("role", "viewer"),
            "is_admin": payload.get("role") == "admin"
        }
    return {"authenticated": False, "role": None, "is_admin": False}
