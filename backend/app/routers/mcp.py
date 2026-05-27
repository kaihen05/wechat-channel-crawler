"""
MCP Server Router for WeChat Channel Aggregator
提供符合 MCP 协议的工具接口
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from typing import List, Optional
from datetime import datetime, timedelta
from app.database import get_db
from app.models import Article, Channel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/mcp", tags=["MCP Server"])


@router.get("/articles/list")
async def list_articles(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(50, ge=1, le=200, description="返回数量"),
    account_id: Optional[int] = Query(None, description="公众号ID"),
    days: Optional[int] = Query(None, description="最近N天"),
    db: Session = Depends(get_db)
):
    """
    MCP工具: list_articles - 获取文章列表
    
    参数:
    - skip: 跳过数量(分页)
    - limit: 返回数量
    - account_id: 公众号ID(可选)
    - days: 最近N天(可选)
    
    返回: 文章列表,包含id、标题、内容链接、作者、创建时间等
    """
    query = db.query(Article).join(Channel)
    
    # 按公众号筛选
    if account_id:
        query = query.filter(Article.channel_id == account_id)
    
    # 按天数筛选
    if days:
        since_date = datetime.now() - timedelta(days=days)
        query = query.filter(Article.create_time >= since_date)
    
    # 按时间倒序
    articles = query.order_by(desc(Article.create_time)).offset(skip).limit(limit).all()
    
    # 转换为MCP格式
    result = []
    for article in articles:
        result.append({
            "article_id": article.id,
            "account_id": article.channel_id,
            "account_name": article.channel.nickname,
            "title": article.title,
            "link": article.link,
            "author": article.author,
            "digest": article.digest,
            "create_time": article.create_time.isoformat() if article.create_time else None,
            "collected_at": article.collected_at.isoformat() if article.collected_at else None,
            "cover_url": article.cover_url
        })
    
    return {
        "success": True,
        "data": result,
        "total": len(result)
    }


@router.get("/articles/search")
async def search_articles(
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(50, ge=1, le=200, description="返回数量"),
    db: Session = Depends(get_db)
):
    """
    MCP工具: search_articles - 搜索文章
    
    参数:
    - keyword: 搜索关键词(必填) - 在标题和摘要中搜索
    - skip: 跳过数量(分页)
    - limit: 返回数量
    
    返回: 匹配的文章列表
    """
    # 构建搜索条件
    query = db.query(Article).join(Channel).filter(
        or_(
            Article.title.contains(keyword),
            Article.digest.contains(keyword),
            Article.author.contains(keyword),
            Channel.nickname.contains(keyword)
        )
    )
    
    # 按时间倒序
    articles = query.order_by(desc(Article.create_time)).offset(skip).limit(limit).all()
    
    # 转换为MCP格式
    result = []
    for article in articles:
        result.append({
            "article_id": article.id,
            "account_id": article.channel_id,
            "account_name": article.channel.nickname,
            "title": article.title,
            "link": article.link,
            "author": article.author,
            "digest": article.digest,
            "create_time": article.create_time.isoformat() if article.create_time else None,
            "collected_at": article.collected_at.isoformat() if article.collected_at else None,
            "cover_url": article.cover_url
        })
    
    return {
        "success": True,
        "data": result,
        "total": len(result),
        "keyword": keyword
    }


@router.get("/articles/{article_id}")
async def get_article(
    article_id: int,
    db: Session = Depends(get_db)
):
    """
    MCP工具: get_article - 获取文章详情
    
    参数:
    - article_id: 文章ID(必填)
    
    返回: 文章完整详情
    """
    article = db.query(Article).join(Channel).filter(Article.id == article_id).first()
    
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    return {
        "success": True,
        "data": {
            "article_id": article.id,
            "account_id": article.channel_id,
            "account_name": article.channel.nickname,
            "title": article.title,
            "link": article.link,
            "content_url": article.content_url,
            "author": article.author,
            "digest": article.digest,
            "cover_url": article.cover_url,
            "create_time": article.create_time.isoformat() if article.create_time else None,
            "collected_at": article.collected_at.isoformat() if article.collected_at else None,
            "channel": {
                "id": article.channel.id,
                "fakeid": article.channel.fakeid,
                "nickname": article.channel.nickname,
                "account_name": article.channel.account_name,
                "round_head_img": article.channel.round_head_img,
                "is_active": article.channel.is_active,
                "last_sync_at": article.channel.last_sync_at.isoformat() if article.channel.last_sync_at else None
            }
        }
    }


@router.get("/accounts/list")
async def list_accounts(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(50, ge=1, le=200, description="返回数量"),
    university_id: Optional[int] = Query(None, description="大学ID(预留)"),
    db: Session = Depends(get_db)
):
    """
    MCP工具: list_accounts - 获取公众号列表
    
    参数:
    - skip: 跳过数量(分页)
    - limit: 返回数量
    - university_id: 大学ID(预留字段,暂未实现)
    
    返回: 公众号列表
    """
    query = db.query(Channel)
    
    # 按时间倒序
    channels = query.order_by(desc(Channel.created_at)).offset(skip).limit(limit).all()
    
    # 转换为MCP格式
    result = []
    for channel in channels:
        # 获取文章数量
        article_count = db.query(Article).filter(Article.channel_id == channel.id).count()
        
        result.append({
            "account_id": channel.id,
            "fakeid": channel.fakeid,
            "nickname": channel.nickname,
            "account_name": channel.account_name,
            "round_head_img": channel.round_head_img,
            "is_active": channel.is_active,
            "article_count": article_count,
            "last_sync_at": channel.last_sync_at.isoformat() if channel.last_sync_at else None,
            "created_at": channel.created_at.isoformat() if channel.created_at else None
        })
    
    return {
        "success": True,
        "data": result,
        "total": len(result)
    }


@router.get("/accounts/{account_id}")
async def get_account(
    account_id: int,
    db: Session = Depends(get_db)
):
    """
    MCP工具: get_account - 获取公众号详情
    
    参数:
    - account_id: 公众号ID(必填)
    
    返回: 公众号完整详情
    """
    channel = db.query(Channel).filter(Channel.id == account_id).first()
    
    if not channel:
        raise HTTPException(status_code=404, detail="公众号不存在")
    
    # 获取最新文章
    recent_articles = db.query(Article).filter(
        Article.channel_id == channel.id
    ).order_by(desc(Article.create_time)).limit(10).all()
    
    # 获取文章数量
    article_count = db.query(Article).filter(Article.channel_id == channel.id).count()
    
    return {
        "success": True,
        "data": {
            "account_id": channel.id,
            "fakeid": channel.fakeid,
            "nickname": channel.nickname,
            "account_name": channel.account_name,
            "round_head_img": channel.round_head_img,
            "is_active": channel.is_active,
            "article_count": article_count,
            "last_sync_at": channel.last_sync_at.isoformat() if channel.last_sync_at else None,
            "created_at": channel.created_at.isoformat() if channel.created_at else None,
            "recent_articles": [
                {
                    "article_id": a.id,
                    "title": a.title,
                    "create_time": a.create_time.isoformat() if a.create_time else None
                }
                for a in recent_articles
            ]
        }
    }


@router.get("/universities/list")
async def list_universities(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(50, ge=1, le=200, description="返回数量")
):
    """
    MCP工具: list_universities - 获取大学列表
    
    参数:
    - skip: 跳过数量(分页)
    - limit: 返回数量
    
    注意: 当前版本暂未实现大学分类功能,此接口返回空列表
    
    返回: 大学列表(预留接口)
    """
    # 预留接口,当前版本返回空列表
    return {
        "success": True,
        "data": [],
        "total": 0,
        "message": "大学分类功能暂未实现,敬请期待"
    }


@router.get("/universities/{university_id}")
async def get_university(
    university_id: int,
    db: Session = Depends(get_db)
):
    """
    MCP工具: get_university - 获取大学详情
    
    参数:
    - university_id: 大学ID(必填)
    
    注意: 当前版本暂未实现大学分类功能
    
    返回: 大学详情(预留接口)
    """
    # 预留接口,当前版本返回404
    raise HTTPException(status_code=404, detail="大学分类功能暂未实现")


@router.get("/info")
async def mcp_info():
    """
    MCP服务器信息
    
    返回: MCP Server的基本信息和可用工具列表
    """
    return {
        "name": "wechat-aggregator",
        "version": "1.0.0",
        "description": "微信公众号聚合器 MCP Server",
        "transport": "HTTP",
        "tools": [
            {
                "name": "list_articles",
                "description": "获取文章列表",
                "parameters": {
                    "skip": {"type": "integer", "description": "跳过数量", "default": 0},
                    "limit": {"type": "integer", "description": "返回数量", "default": 50},
                    "account_id": {"type": "integer", "description": "公众号ID", "optional": True},
                    "days": {"type": "integer", "description": "最近N天", "optional": True}
                }
            },
            {
                "name": "search_articles",
                "description": "搜索文章",
                "parameters": {
                    "keyword": {"type": "string", "description": "搜索关键词", "required": True},
                    "skip": {"type": "integer", "description": "跳过数量", "default": 0},
                    "limit": {"type": "integer", "description": "返回数量", "default": 50}
                }
            },
            {
                "name": "get_article",
                "description": "获取文章详情",
                "parameters": {
                    "article_id": {"type": "integer", "description": "文章ID", "required": True}
                }
            },
            {
                "name": "list_accounts",
                "description": "获取公众号列表",
                "parameters": {
                    "skip": {"type": "integer", "description": "跳过数量", "default": 0},
                    "limit": {"type": "integer", "description": "返回数量", "default": 50},
                    "university_id": {"type": "integer", "description": "大学ID", "optional": True}
                }
            },
            {
                "name": "get_account",
                "description": "获取公众号详情",
                "parameters": {
                    "account_id": {"type": "integer", "description": "公众号ID", "required": True}
                }
            },
            {
                "name": "list_universities",
                "description": "获取大学列表",
                "parameters": {
                    "skip": {"type": "integer", "description": "跳过数量", "default": 0},
                    "limit": {"type": "integer", "description": "返回数量", "default": 50}
                }
            },
            {
                "name": "get_university",
                "description": "获取大学详情",
                "parameters": {
                    "university_id": {"type": "integer", "description": "大学ID", "required": True}
                }
            }
        ]
    }
