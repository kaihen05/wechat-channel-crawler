from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import pandas as pd
from app.database import get_db
from app.models import Channel
from app.schemas.channel import (
    ChannelCreate,
    ChannelResponse,
    ChannelUpdate,
    ChannelSearchResult
)
from app.services.wechat_crawler import WeChatCrawler, WeChatSessionError
from app.services.ai_classifier import auto_classify_channel
from app.services.ai_university_classifier import auto_classify_university, university_classifier
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/channels", tags=["公众号管理"])


@router.get("", response_model=List[ChannelResponse])
async def get_channels(
    is_active: bool = None,
    category: str = None,
    db: Session = Depends(get_db)
):
    """获取所有公众号"""
    query = db.query(Channel)

    if is_active is not None:
        query = query.filter(Channel.is_active == is_active)

    if category:
        query = query.filter(Channel.category == category)

    # 按分类排序：综合、技术、游戏、产品、人力、未分类，同分类按创建时间降序
    from sqlalchemy import case
    category_order = case(
        (Channel.category == '综合', 1),
        (Channel.category == '技术', 2),
        (Channel.category == '游戏', 3),
        (Channel.category == '产品', 4),
        (Channel.category == '人力', 5),
        (Channel.category == '未分类', 6),
        else_=7
    )
    channels = query.order_by(category_order, Channel.created_at.desc()).all()
    return channels


@router.post("", response_model=ChannelResponse)
async def create_channel(
    channel: ChannelCreate,
    db: Session = Depends(get_db)
):
    """添加公众号"""
    # 检查是否已存在
    existing = db.query(Channel).filter(Channel.fakeid == channel.fakeid).first()
    if existing:
        raise HTTPException(status_code=400, detail="公众号已存在")
    
    db_channel = Channel(**channel.dict())
    db.add(db_channel)
    db.commit()
    db.refresh(db_channel)
    
    return db_channel


@router.post("/search")
async def search_channels(
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    db: Session = Depends(get_db)
):
    """搜索公众号"""
    try:
        if not settings.wechat_token or not settings.wechat_cookie:
            raise HTTPException(status_code=400, detail="未配置微信凭证")

        crawler = WeChatCrawler(settings.wechat_token, settings.wechat_cookie)
        results = crawler.search_accounts(keyword, limit=20)

        return [
            ChannelSearchResult(
                fakeid=r["fakeid"],
                nickname=r["nickname"],
                round_head_img=r.get("round_head_img"),
                account_name=r.get("account_name")
            )
            for r in results
        ]
    except WeChatSessionError as e:
        logger.error(f"微信凭证过期: {e}")
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"搜索公众号失败: {e}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.post("/classify")
async def classify_channel(
    nickname: str = Query(..., description="公众号名称"),
    description: str = Query(None, description="公众号描述（可选）")
):
    """AI自动分类"""
    try:
        category = await auto_classify_channel(nickname, description or "")
        return {
            "nickname": nickname,
            "category": category,
            "method": "AI" if settings.deepseek_api_key else "关键词"
        }
    except Exception as e:
        logger.error(f"AI分类失败: {e}")
        raise HTTPException(status_code=500, detail=f"分类失败: {str(e)}")


@router.post("/identify-university")
async def identify_university(
    nickname: str = Query(..., description="公众号名称"),
    description: str = Query(None, description="公众号描述（可选）")
):
    """AI自动识别学校"""
    try:
        university = await auto_classify_university(nickname, description or "")
        return {
            "nickname": nickname,
            "university": university,
            "method": "AI" if settings.deepseek_api_key else "关键词"
        }
    except Exception as e:
        logger.error(f"学校识别失败: {e}")
        raise HTTPException(status_code=500, detail=f"学校识别失败: {str(e)}")


@router.get("/universities", response_model=List[str])
async def get_universities():
    """获取所有可用的学校列表"""
    return university_classifier.get_all_universities()


@router.put("/{channel_id}", response_model=ChannelResponse)
async def update_channel(
    channel_id: int,
    update: ChannelUpdate,
    db: Session = Depends(get_db)
):
    """更新公众号"""
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="公众号不存在")

    if update.is_active is not None:
        channel.is_active = update.is_active

    if update.university_name is not None:
        channel.university_name = update.university_name

    if update.category is not None:
        # 允许自定义分类，不再限制为固定值
        channel.category = update.category

    if update.is_competitor is not None:
        channel.is_competitor = update.is_competitor

    if update.competitor_keywords is not None:
        channel.competitor_keywords = update.competitor_keywords

    if update.competitor_note is not None:
        channel.competitor_note = update.competitor_note

    db.commit()
    db.refresh(channel)

    return channel


@router.delete("/{channel_id}")
async def delete_channel(
    channel_id: int,
    db: Session = Depends(get_db)
):
    """删除公众号"""
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="公众号不存在")
    
    db.delete(channel)
    db.commit()
    
    return {"success": True, "message": "删除成功"}


@router.post("/import")
async def import_channels_from_excel(
    file: UploadFile = File(..., description="Excel文件"),
    db: Session = Depends(get_db)
):
    """从Excel批量导入公众号"""
    try:
        logger.info(f"开始导入Excel文件: {file.filename}")

        # 读取Excel文件
        import io
        content = await file.read()
        logger.info(f"读取文件大小: {len(content)} bytes")

        df = pd.read_excel(io.BytesIO(content))
        logger.info(f"Excel解析成功, 列: {list(df.columns)}, 行数: {len(df)}")

        # 验证必需的列
        required_columns = ['fakeid', 'nickname', 'category']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Excel文件缺少必需的列: {', '.join(missing_columns)}。必需列: fakeid, nickname, category"
            )

        # 不再验证分类，允许自定义分类

        # 导入数据
        success_count = 0
        skipped_count = 0
        error_messages = []

        for _, row in df.iterrows():
            try:
                fakeid = str(row['fakeid']).strip()
                nickname = str(row['nickname']).strip()
                category = str(row['category']).strip()
                account_name = str(row.get('account_name', '')).strip() if pd.notna(row.get('account_name')) else None
                avatar_url = str(row.get('avatar_url', '')).strip() if pd.notna(row.get('avatar_url')) else None
                university_name = str(row.get('university_name', '')).strip() if pd.notna(row.get('university_name')) else ""

                # 检查是否已存在
                existing = db.query(Channel).filter(Channel.fakeid == fakeid).first()
                if existing:
                    skipped_count += 1
                    continue

                # 创建新公众号
                channel = Channel(
                    fakeid=fakeid,
                    nickname=nickname,
                    account_name=account_name,
                    avatar_url=avatar_url,
                    university_name=university_name,
                    category=category,
                    is_active=True
                )
                db.add(channel)
                success_count += 1

            except Exception as e:
                error_messages.append(f"第{_ + 2}行错误: {str(e)}")
                logger.error(f"导入公众号失败: {e}")

        db.commit()

        return {
            "success": True,
            "message": f"成功导入 {success_count} 个公众号，跳过 {skipped_count} 个已存在的公众号",
            "stats": {
                "total": len(df),
                "success": success_count,
                "skipped": skipped_count,
                "errors": len(error_messages)
            },
            "errors": error_messages
        }

    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="Excel文件为空")
    except Exception as e:
        db.rollback()
        logger.error(f"导入Excel失败: {e}")
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")


@router.post("/add-by-search", response_model=ChannelResponse)
async def add_channel_by_search(
    keyword: str = Query(..., min_length=1, description="公众号名称关键词"),
    category: str = Query("未分类", description="分类"),
    university_name: str = Query("", description="学校名称"),
    db: Session = Depends(get_db)
):
    """通过名称搜索并添加公众号（自动获取fakeid）"""
    try:
        if not settings.wechat_token or not settings.wechat_cookie:
            raise HTTPException(status_code=400, detail="未配置微信凭证")

        # 1. 搜索公众号
        crawler = WeChatCrawler(settings.wechat_token, settings.wechat_cookie)
        results = crawler.search_accounts(keyword, limit=5)

        if not results:
            raise HTTPException(status_code=404, detail=f"未找到公众号: {keyword}")

        # 2. 取最佳匹配（优先完全匹配nickname，否则取第一个）
        best_match = None
        for r in results:
            if r.get("nickname") == keyword:
                best_match = r
                break
        if not best_match:
            best_match = results[0]

        fakeid = best_match.get("fakeid")
        nickname = best_match.get("nickname", keyword)
        account_name = best_match.get("account_name", "")
        avatar_url = best_match.get("round_head_img", "")

        if not fakeid or fakeid == "zonghe_test":
            raise HTTPException(status_code=400, detail=f"获取到的fakeid无效: {fakeid}")

        # 3. 检查是否已存在
        existing = db.query(Channel).filter(Channel.fakeid == fakeid).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"公众号已存在: {nickname}")

        # 4. AI自动分类（如果未指定或默认分类）
        final_category = category
        if final_category in ("未分类", "选择分类（可选）"):
            try:
                final_category = await auto_classify_channel(nickname, "")
            except Exception:
                final_category = "未分类"

        # 5. AI自动识别学校（如果未指定）
        final_university = university_name
        if not final_university:
            try:
                final_university = await auto_classify_university(nickname, "")
            except Exception:
                final_university = ""

        # 6. 创建公众号（自动开启友商监控）
        channel = Channel(
            fakeid=fakeid,
            nickname=nickname,
            account_name=account_name or None,
            avatar_url=avatar_url or None,
            university_name=final_university,
            category=final_category,
            is_active=True,
            is_competitor=True,  # 自动开启友商监控
            competitor_keywords="",  # 使用默认关键词
            competitor_note="自动开启"
        )
        db.add(channel)
        db.commit()
        db.refresh(channel)

        logger.info(f"通过搜索添加公众号: {nickname} (fakeid={fakeid}, category={final_category}, university={final_university}, 友商监控=已开启)")
        return channel

    except WeChatSessionError as e:
        logger.error(f"微信凭证过期: {e}")
        raise HTTPException(status_code=401, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加公众号失败: {e}")
        raise HTTPException(status_code=500, detail=f"添加失败: {str(e)}")


@router.get("/categories", response_model=List[str])
async def get_categories():
    """获取所有可用的分类"""
    return ['综合', '技术', '游戏', '产品', '人力']


@router.post("/refresh-avatars")
async def refresh_avatars(
    force: bool = Query(False, description="强制刷新所有头像，即使已有头像也重新获取"),
    db: Session = Depends(get_db)
):
    """批量刷新公众号头像"""
    if not settings.wechat_token or not settings.wechat_cookie:
        raise HTTPException(status_code=400, detail="未配置微信凭证")

    if force:
        channels = db.query(Channel).all()
    else:
        channels = db.query(Channel).filter(
            (Channel.avatar_url == None) | (Channel.avatar_url == '')
        ).all()

    if not channels:
        return {"success": True, "message": "所有公众号已有头像", "updated": 0}

    crawler = WeChatCrawler(settings.wechat_token, settings.wechat_cookie)
    updated = 0
    errors = []

    for channel in channels:
        try:
            results = crawler.search_accounts(channel.nickname, limit=5)
            for r in results:
                if r.get("fakeid") == channel.fakeid or r.get("nickname") == channel.nickname:
                    avatar_url = r.get("round_head_img", "")
                    if avatar_url:
                        channel.avatar_url = avatar_url
                        updated += 1
                    break
        except Exception as e:
            errors.append(f"{channel.nickname}: {str(e)}")
            logger.error(f"刷新头像失败 {channel.nickname}: {e}")

    db.commit()

    return {
        "success": True,
        "message": f"已更新 {updated} 个公众号头像",
        "updated": updated,
        "total": len(channels),
        "errors": errors[:10]
    }
