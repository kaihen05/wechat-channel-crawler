from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ChannelBase(BaseModel):
    """公众号基础模型"""
    fakeid: str = Field(..., description="公众号唯一标识")
    nickname: str = Field(..., description="公众号名称")
    account_name: Optional[str] = Field(None, description="公众号账号名")
    avatar_url: Optional[str] = Field(None, description="头像URL")
    category: Optional[str] = Field("未分类", description="分类: 综合/技术/游戏/产品/人力/未分类")


class ChannelCreate(ChannelBase):
    """创建公众号"""
    pass


class ChannelUpdate(BaseModel):
    """更新公众号"""
    is_active: Optional[bool] = Field(None, description="是否启用")
    category: Optional[str] = Field(None, description="分类: 综合/技术/游戏/产品/人力/未分类")
    university_name: Optional[str] = Field(None, description="大学名称")
    is_competitor: Optional[bool] = Field(None, description="是否为友商公众号")
    competitor_keywords: Optional[str] = Field(None, description="检测关键词（逗号分隔）")
    competitor_note: Optional[str] = Field(None, description="备注")


class ChannelResponse(ChannelBase):
    """公众号响应"""
    id: int
    category: str
    university_name: Optional[str] = ""
    is_active: bool
    is_competitor: bool = False
    competitor_keywords: str = ""
    competitor_note: str = ""
    total_read_num: int = 0
    created_at: datetime
    updated_at: datetime
    last_sync_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChannelSearchResult(BaseModel):
    """公众号搜索结果"""
    fakeid: str
    nickname: str
    round_head_img: Optional[str] = None
    account_name: Optional[str] = None
