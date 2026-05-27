from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.config import settings
from app.services.wechat_crawler import test_credentials
from datetime import datetime

router = APIRouter(prefix="/api/auth", tags=["认证"])


class CredentialsRequest(BaseModel):
    token: str
    cookie: str


@router.post("/credentials")
async def set_credentials(
    request: CredentialsRequest,
    db: Session = Depends(get_db)
):
    """设置微信公众号登录凭证"""
    # 验证凭证
    result = test_credentials(request.token, request.cookie)
    
    if not result["valid"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    # 更新配置（实际应用中应该保存到数据库）
    settings.wechat_token = request.token
    settings.wechat_cookie = request.cookie
    
    return {
        "success": True,
        "message": "凭证设置成功",
        "checked_at": result["checked_at"]
    }


@router.get("/credentials/status")
async def get_credentials_status():
    """获取凭证状态"""
    if not settings.wechat_token or not settings.wechat_cookie:
        return {
            "configured": False,
            "message": "未配置凭证"
        }
    
    # 测试凭证
    result = test_credentials(settings.wechat_token, settings.wechat_cookie)
    
    return {
        "configured": True,
        "valid": result["valid"],
        "message": result["message"],
        "checked_at": result["checked_at"]
    }
