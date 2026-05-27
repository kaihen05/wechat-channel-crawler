from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, Body
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from datetime import datetime, timedelta
from app.database import get_db, SessionLocal
from app.models import Article, Channel
from app.schemas.article import ArticleResponse, ArticleListResponse
from app.services.wechat_crawler import WeChatCrawler
from app.config import settings
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/articles", tags=["文章管理"])

# 线程池用于执行同步阻塞操作
_executor = ThreadPoolExecutor(max_workers=2)


def _sync_all_articles():
    """在后台线程中执行同步操作"""
    db = SessionLocal()
    try:
        if not settings.wechat_token or not settings.wechat_cookie:
            logger.warning("未配置微信凭证，跳过同步")
            return

        channels = db.query(Channel).filter(Channel.is_active == True).all()
        if not channels:
            logger.warning("没有启用的公众号，跳过同步")
            return

        logger.info(f"[后台同步] 准备同步 {len(channels)} 个公众号")
        crawler = WeChatCrawler(settings.wechat_token, settings.wechat_cookie)
        total_articles = 0
        errors = []

        for channel in channels:
            try:
                articles = crawler.get_articles(
                    fakeid=channel.fakeid,
                    days=settings.default_days,
                    count=settings.max_articles_per_account
                )
                count = 0
                updated_count = 0
                for article_data in articles:
                    content_url = article_data.get("content_url")
                    if not content_url:
                        continue
                    existing = db.query(Article).filter(
                        Article.content_url == content_url
                    ).first()
                    if existing:
                        new_read_num = article_data.get("read_num", 0)
                        if existing.read_num != new_read_num:
                            existing.read_num = new_read_num
                            updated_count += 1
                    else:
                        article = Article(
                            channel_id=channel.id,
                            title=article_data.get("title", ""),
                            content_url=content_url,
                            link=article_data.get("link", ""),
                            digest=article_data.get("digest"),
                            author=article_data.get("author"),
                            cover_url=article_data.get("cover"),
                            create_time=article_data.get("create_time"),
                            read_num=article_data.get("read_num", 0)
                        )
                        db.add(article)
                        count += 1
                db.flush()
                total_reads = db.query(Article).filter(
                    Article.channel_id == channel.id
                ).with_entities(func.sum(Article.read_num)).scalar() or 0
                channel.total_read_num = total_reads
                channel.last_sync_at = datetime.now()
                db.commit()
                total_articles += count
                logger.info(f"[后台同步] 公众号 '{channel.nickname}' 完成，新增 {count} 篇，更新 {updated_count} 篇")
            except Exception as e:
                logger.error(f"[后台同步] 公众号 '{channel.nickname}' 失败: {e}")
                errors.append(f"{channel.nickname}: {str(e)}")
                db.rollback()

        logger.info(f"[后台同步] 全部完成，新增 {total_articles} 篇文章，错误: {len(errors)}")
    finally:
        db.close()


@router.get("")
async def get_articles(
    channel_id: Optional[int] = Query(None, description="公众号ID"),
    category: Optional[str] = Query(None, description="分类: 游戏/产品/人力/技术"),
    university: Optional[str] = Query(None, description="学校名称"),
    days: Optional[int] = Query(None, ge=1, description="最近N天"),
    limit: int = Query(50, ge=1, le=200, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: Session = Depends(get_db)
):
    """获取文章列表"""
    # 强制重新加载测试
    query = db.query(Article).join(Channel)

    if channel_id:
        query = query.filter(Article.channel_id == channel_id)

    if category:
        query = query.filter(Channel.category == category)

    if university:
        query = query.filter(Channel.university_name == university)

    if days:
        days_ago = datetime.now() - timedelta(days=days)
        query = query.filter(Article.create_time >= days_ago)

    articles = query.order_by(desc(Article.create_time)).offset(offset).limit(limit).all()

    # 转换为响应格式
    result = []
    for article in articles:
        article_dict = {
            "id": article.id,
            "channel_id": article.channel_id,
            "title": article.title,
            "link": article.link,
            "author": article.author or "未知作者",
            "create_time": article.create_time,
            "collected_at": article.collected_at,
            "channel_name": article.channel.nickname,
            "account_name": article.channel.account_name or article.channel.nickname,
            "university_name": article.channel.university_name or "",
            "category": article.channel.category or "未分类",
            "read_num": article.read_num or 0,
        }
        # 添加公众号累计阅读量
        if hasattr(article.channel, 'total_read_num') and article.channel.total_read_num is not None:
            article_dict["channel_total_read_num"] = article.channel.total_read_num
        else:
            article_dict["channel_total_read_num"] = 0

        if article.digest:
            article_dict["digest"] = article.digest

        result.append(article_dict)

    return result


@router.post("/sync")
async def sync_articles(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """同步所有启用公众号的文章（后台异步执行）"""
    try:
        if not settings.wechat_token or not settings.wechat_cookie:
            raise HTTPException(status_code=400, detail="未配置微信凭证")

        channels = db.query(Channel).filter(Channel.is_active == True).all()
        if not channels:
            raise HTTPException(status_code=400, detail="没有启用的公众号")

        # 提交到线程池后台执行，立即返回
        loop = asyncio.get_event_loop()
        loop.run_in_executor(_executor, _sync_all_articles)

        return {
            "success": True,
            "message": f"同步任务已提交，共 {len(channels)} 个公众号将在后台同步",
            "total_articles": 0,
            "channels_synced": len(channels)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"启动同步任务失败: {e}")
        raise HTTPException(status_code=500, detail=f"启动同步失败: {str(e)}")


@router.get("/stats")
async def get_article_stats(db: Session = Depends(get_db)):
    """获取文章统计信息"""
    total = db.query(Article).count()
    today = db.query(Article).filter(
        Article.collected_at >= datetime.now().date()
    ).count()

    channels = db.query(Channel).filter(Channel.is_active == True).count()

    return {
        "total_articles": total,
        "today_articles": today,
        "active_channels": channels
    }


@router.post("/update-read-nums")
async def update_channel_read_nums(db: Session = Depends(get_db)):
    """更新所有公众号的累计阅读量"""
    try:
        logger.info("开始更新所有公众号的累计阅读量")

        channels = db.query(Channel).all()
        updated_count = 0

        for channel in channels:
            # 计算该公众号所有文章的总阅读量
            total_reads = db.query(Article).filter(
                Article.channel_id == channel.id
            ).with_entities(
                func.sum(Article.read_num)
            ).scalar() or 0

            if channel.total_read_num != total_reads:
                channel.total_read_num = total_reads
                updated_count += 1
                logger.info(f"更新公众号 '{channel.nickname}' 累计阅读量: {channel.total_read_num} -> {total_reads}")

        db.commit()

        logger.info(f"累计阅读量更新完成，共更新 {updated_count} 个公众号")

        return {
            "success": True,
            "message": f"成功更新 {updated_count} 个公众号的累计阅读量",
            "updated_count": updated_count,
            "total_channels": len(channels)
        }

    except Exception as e:
        logger.error(f"更新累计阅读量失败: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")


@router.post("/sync-batch")
async def sync_batch_articles(
    batch_index: int = Body(..., description="当前批次索引（0开始）"),
    total_batches: int = Body(..., description="总批次数"),
    batch_size: int = Body(default=30, description="每批大小"),
    db: Session = Depends(get_db)
):
    """
    分批次同步公众号文章（用于解决微信频率限制问题）

    - 将公众号按 ID 顺序分批
    - batch_index=0 同步第 0~batch_size 个公众号
    - batch_index=1 同步第 batch_size~2*batch_size 个公众号
    - 以此类推，实现轮转式分批同步
    """
    try:
        if not settings.wechat_token or not settings.wechat_cookie:
            raise HTTPException(status_code=400, detail="未配置微信凭证")

        # 按 ID 顺序获取所有启用的公众号
        channels = db.query(Channel).filter(
            Channel.is_active == True
        ).order_by(Channel.id).all()

        if not channels:
            raise HTTPException(status_code=400, detail="没有启用的公众号")

        # 计算本批次要同步的公众号范围
        start_idx = batch_index * batch_size
        end_idx = min(start_idx + batch_size, len(channels))

        if start_idx >= len(channels):
            logger.info(f"[批次同步] batch_index={batch_index} 超出范围，跳过")
            return {
                "success": True,
                "message": f"批次 {batch_index + 1}/{total_batches} 无可同步的公众号",
                "total_articles": 0,
                "channels_synced": 0
            }

        batch_channels = channels[start_idx:end_idx]

        logger.info(f"[批次同步] 批次 {batch_index + 1}/{total_batches}，同步公众号 {start_idx + 1}~{end_idx}，共 {len(batch_channels)} 个")

        # 在后台线程执行本批次同步
        loop = asyncio.get_event_loop()
        loop.run_in_executor(
            _executor,
            _sync_batch_articles,
            batch_channels
        )

        return {
            "success": True,
            "message": f"批次同步任务已提交，同步公众号 {start_idx + 1}~{end_idx}",
            "total_articles": 0,
            "channels_synced": len(batch_channels),
            "batch_info": {
                "batch_index": batch_index,
                "total_batches": total_batches,
                "start_idx": start_idx,
                "end_idx": end_idx,
                "channels_in_batch": len(batch_channels)
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"启动批次同步任务失败: {e}")
        raise HTTPException(status_code=500, detail=f"启动批次同步失败: {str(e)}")


def _sync_batch_articles(batch_channels):
    """在后台线程中执行指定批次公众号的同步"""
    db = SessionLocal()
    try:
        if not settings.wechat_token or not settings.wechat_cookie:
            logger.warning("未配置微信凭证，跳过同步")
            return

        logger.info(f"[批次后台同步] 准备同步 {len(batch_channels)} 个公众号")
        crawler = WeChatCrawler(settings.wechat_token, settings.wechat_cookie)

        # 进入批次模式：减少延迟以加快同步速度
        crawler.enter_batch_mode()

        total_articles = 0
        errors = []

        for channel in batch_channels:
            try:
                articles = crawler.get_articles(
                    fakeid=channel.fakeid,
                    days=settings.default_days,
                    count=settings.max_articles_per_account
                )
                count = 0
                updated_count = 0
                for article_data in articles:
                    content_url = article_data.get("content_url")
                    if not content_url:
                        continue
                    existing = db.query(Article).filter(
                        Article.content_url == content_url
                    ).first()
                    if existing:
                        new_read_num = article_data.get("read_num", 0)
                        if existing.read_num != new_read_num:
                            existing.read_num = new_read_num
                            updated_count += 1
                    else:
                        article = Article(
                            channel_id=channel.id,
                            title=article_data.get("title", ""),
                            content_url=content_url,
                            link=article_data.get("link", ""),
                            digest=article_data.get("digest"),
                            author=article_data.get("author"),
                            cover_url=article_data.get("cover"),
                            create_time=article_data.get("create_time"),
                            read_num=article_data.get("read_num", 0)
                        )
                        db.add(article)
                        count += 1
                db.flush()
                total_reads = db.query(Article).filter(
                    Article.channel_id == channel.id
                ).with_entities(func.sum(Article.read_num)).scalar() or 0
                channel.total_read_num = total_reads
                channel.last_sync_at = datetime.now()
                db.commit()
                total_articles += count
                logger.info(f"[批次后台同步] 公众号 '{channel.nickname}' 完成，新增 {count} 篇，更新 {updated_count} 篇")
            except Exception as e:
                logger.error(f"[批次后台同步] 公众号 '{channel.nickname}' 失败: {e}")
                errors.append(f"{channel.nickname}: {str(e)}")
                db.rollback()

        logger.info(f"[批次后台同步] 全部完成，新增 {total_articles} 篇文章，错误: {len(errors)}")
    finally:
        crawler.exit_batch_mode()
        db.close()
