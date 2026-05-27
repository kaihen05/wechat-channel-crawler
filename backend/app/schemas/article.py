from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ArticleBase(BaseModel):
    """文章基础模型"""
    title: str = Field(..., description="文章标题")
    content_url: str = Field(..., description="文章内容URL")
    link: str = Field(..., description="文章链接")
    digest: Optional[str] = Field(None, description="文章摘要")
    author: Optional[str] = Field(None, description="作者")
    cover_url: Optional[str] = Field(None, description="封面图URL")
    create_time: datetime = Field(..., description="文章发布时间")


class ArticleResponse(ArticleBase):
    """文章响应"""
    id: int
    channel_id: int
    collected_at: datetime
    
    class Config:
        from_attributes = True


class ArticleListResponse(BaseModel):
    """文章列表响应（带公众号名称）"""
    id: int
    channel_id: int
    title: str
    link: str
    author: Optional[str]
    create_time: datetime
    collected_at: datetime
    channel_name: str  # 公众号名称
    account_name: Optional[str]  # 公众号账号名
    category: Optional[str]  # 分类
    digest: Optional[str] = None  # 摘要
