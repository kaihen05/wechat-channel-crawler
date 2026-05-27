from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import List, Optional
from app.database import get_db
from app.models import Article, Channel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analysis", tags=["AI分析"])

# 友商名称关键词（公司/品牌名）
COMPETITOR_NAMES = [
    "网易", "腾讯", "阿里", "字节", "百度", "京东", "美团",
    "华为", "小米", "米哈游", "莉莉丝", "鹰角", "叠纸",
    "哔哩哔哩", "b站", "快手", "抖音",
    "雷火", "互娱", "天美", "光子", "魔方",
    "完美世界", "盛趣", "巨人", "游族", "三七互娱",
    "育碧", "暴雪", "拳头",
    "英特尔", "英伟达", "nvidia", "amd",
    "unity", "unreal", "虚幻",
]

# 合作类关键词（必须同时出现才算友商合作）
COOPERATION_KEYWORDS = [
    "赞助", "冠名", "合作", "联合主办", "承办", "协办",
    "联合举办", "战略", "签约", "携手", "联动", "共建",
    "独家", "伙伴", "支持单位",
]

# 全局关键词（单独出现即算，如比赛名称中含友商名）
COMPETITOR_KEYWORDS = COMPETITOR_NAMES + COOPERATION_KEYWORDS


def _detect_competitor_cooperation(title: str, digest: Optional[str]) -> bool:
    """
    检测文章是否包含友商合作信息
    逻辑：必须同时满足
      1. 包含至少一个友商名称
      2. 包含至少一个合作类词汇
    或者标题中包含明显的比赛/活动+友商名（如"网易游戏高校挑战赛"）
    """
    text = (title or "") + " " + (digest or "")
    text_lower = text.lower()

    # 检查是否包含友商名称
    has_competitor = any(name in text_lower for name in COMPETITOR_NAMES)
    # 检查是否包含合作类词汇
    has_cooperation = any(kw in text_lower for kw in COOPERATION_KEYWORDS)

    # 同时满足：友商名称 + 合作词汇
    if has_competitor and has_cooperation:
        return True

    # 特殊模式：友商名 + 招聘/活动/比赛类词汇
    event_patterns = [
        # 招聘求职类
        "招聘", "校招", "春招", "秋招", "社招", "内推", "宣讲", "宣讲会",
        "offer", "求职", "面试", "实习", "入职",
        # 比赛活动类
        "挑战", "大赛", "比赛", "活动", "竞赛", "赛事", "赛", "报名",
        "极限开发", "gamejam", "game jam", "jam",
        # 宣讲分享类
        "分享", "分享会", "沙龙", "讲座", "论坛", "open day", "openday",
        "企业", "公司", "职场", "职业", "工作坊",
        # 其他合作形式
        "冠名", "赞助", "承办", "协办", "联合主办", "联合举办", "合作",
    ]
    if has_competitor:
        for pat in event_patterns:
            if pat in text_lower:
                return True

    return False


def _get_matched_keywords(title: str, digest: Optional[str]) -> list:
    """获取文章匹配到的友商关键词列表（用于展示）"""
    text = (title or "") + " " + (digest or "")
    text_lower = text.lower()
    matched = []
    for kw in COMPETITOR_KEYWORDS:
        if kw in text_lower and kw not in matched:
            matched.append(kw)
    return matched


@router.get("/recommend")
async def get_ai_recommendations(
    school: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    AI推荐：分析各协会/公众号的综合价值

    评分指标：
    1. 活跃度（半年内文章数）- 权重30%
    2. 友商合作度（含友商关键词的文章比例）- 权重30%
    3. 影响力（平均阅读量/总阅读量）- 权重40%
    """
    try:
        six_months_ago = datetime.now() - timedelta(days=180)

        # 基础查询：半年内有文章的公众号
        query = db.query(Channel).filter(Channel.is_active == True)

        if school:
            query = query.filter(Channel.university_name == school)
        if category:
            query = query.filter(Channel.category == category)

        channels = query.all()

        if not channels:
            return {
                "success": True,
                "recommendations": [],
                "message": "未找到符合条件的公众号"
            }

        results = []

        for channel in channels:
            # 1. 半年内文章数
            articles = db.query(Article).filter(
                Article.channel_id == channel.id,
                Article.create_time >= six_months_ago
            ).all()

            article_count = len(articles)
            if article_count == 0:
                continue  # 跳过半年内无文章的公众号

            # 2. 友商合作文章数
            competitor_count = sum(
                1 for a in articles
                if _detect_competitor_cooperation(a.title, a.digest)
            )
            competitor_ratio = competitor_count / article_count if article_count > 0 else 0

            # 3. 阅读量统计
            total_reads = sum(a.read_num or 0 for a in articles)
            avg_reads = total_reads / article_count if article_count > 0 else 0

            # 4. 计算综合评分（0-100）
            # 活跃度分：文章数越多越高，封顶30分（半年30篇=满分）
            activity_score = min(article_count / 30 * 30, 30)

            # 友商合作分：合作文章比例越高越高，封顶30分
            cooperation_score = competitor_ratio * 30

            # 影响力分：平均阅读量，封顶40分（平均5000阅读=满分）
            influence_score = min(avg_reads / 5000 * 40, 40)

            total_score = round(activity_score + cooperation_score + influence_score, 1)

            # 最近3篇代表性文章
            recent_articles = sorted(articles, key=lambda x: x.create_time or datetime.min, reverse=True)[:3]

            results.append({
                "channel_id": channel.id,
                "nickname": channel.nickname,
                "university_name": channel.university_name or "",
                "category": channel.category or "未分类",
                "total_score": total_score,
                "activity_score": round(activity_score, 1),
                "cooperation_score": round(cooperation_score, 1),
                "influence_score": round(influence_score, 1),
                "article_count": article_count,
                "competitor_article_count": competitor_count,
                "competitor_ratio": round(competitor_ratio * 100, 1),
                "total_reads": total_reads,
                "avg_reads": round(avg_reads, 0),
                "recent_articles": [
                    {
                        "title": a.title[:50] + "..." if len(a.title) > 50 else a.title,
                        "create_time": a.create_time.strftime("%Y-%m-%d") if a.create_time else "",
                        "read_num": a.read_num or 0,
                        "is_competitor_related": _detect_competitor_cooperation(a.title, a.digest)
                    }
                    for a in recent_articles
                ]
            })

        # 按总分排序
        results.sort(key=lambda x: x["total_score"], reverse=True)

        # 添加排名
        for i, r in enumerate(results, 1):
            r["rank"] = i

        return {
            "success": True,
            "recommendations": results[:10],  # 只返回前10
            "total_count": len(results),
            "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "message": f"共分析 {len(results)} 个公众号，推荐前 {min(10, len(results))} 个"
        }

    except Exception as e:
        logger.error(f"AI推荐分析失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.get("/recommend/{channel_id}")
async def get_channel_analysis(
    channel_id: int,
    db: Session = Depends(get_db)
):
    """获取单个公众号的详细分析"""
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="公众号不存在")

    six_months_ago = datetime.now() - timedelta(days=180)

    articles = db.query(Article).filter(
        Article.channel_id == channel_id,
        Article.create_time >= six_months_ago
    ).order_by(desc(Article.create_time)).all()

    article_count = len(articles)
    competitor_count = sum(
        1 for a in articles
        if _detect_competitor_cooperation(a.title, a.digest)
    )
    total_reads = sum(a.read_num or 0 for a in articles)
    avg_reads = total_reads / article_count if article_count > 0 else 0

    # 月度趋势
    monthly_trend = {}
    for a in articles:
        month = a.create_time.strftime("%Y-%m") if a.create_time else "未知"
        if month not in monthly_trend:
            monthly_trend[month] = {"count": 0, "reads": 0}
        monthly_trend[month]["count"] += 1
        monthly_trend[month]["reads"] += a.read_num or 0

    return {
        "success": True,
        "channel": {
            "id": channel.id,
            "nickname": channel.nickname,
            "university_name": channel.university_name or "",
            "category": channel.category or "未分类",
        },
        "stats": {
            "article_count": article_count,
            "competitor_article_count": competitor_count,
            "competitor_ratio": round(competitor_count / article_count * 100, 1) if article_count > 0 else 0,
            "total_reads": total_reads,
            "avg_reads": round(avg_reads, 0),
        },
        "monthly_trend": monthly_trend,
        "recent_articles": [
            {
                "title": a.title,
                "create_time": a.create_time.strftime("%Y-%m-%d") if a.create_time else "",
                "read_num": a.read_num or 0,
                "is_competitor_related": _detect_competitor_cooperation(a.title, a.digest)
            }
            for a in articles[:10]
        ]
    }


@router.get("/competitor-monitor")
async def get_competitor_articles(
    days: int = 90,
    limit: int = 0,
    db: Session = Depends(get_db)
):
    """
    友商监控中心：获取包含友商合作信息的文章
    检测逻辑：文章必须同时包含友商名称 + 合作类词汇
    默认查询最近3个月（90天）的所有文章
    """
    try:
        from_date = datetime.now() - timedelta(days=days)

        # 获取被标记为友商的公众号的自定义关键词
        custom_names = []
        custom_coop = []
        competitor_channels = db.query(Channel).filter(Channel.is_competitor == True).all()
        for ch in competitor_channels:
            if ch.competitor_keywords:
                kws = [k.strip() for k in ch.competitor_keywords.split(",") if k.strip()]
                custom_names.extend(kws)

        # 合并全局友商名称和自定义名称
        all_competitor_names = set(COMPETITOR_NAMES + custom_names)

        # 获取最近文章（limit=0表示不限制，返回所有）
        query = db.query(Article).filter(
            Article.create_time >= from_date
        ).order_by(desc(Article.create_time))
        if limit > 0:
            query = query.limit(limit)
        articles = query.all()

        results = []
        for article in articles:
            # 使用严格的检测逻辑
            if not _detect_competitor_cooperation(article.title, article.digest):
                continue

            matched_keywords = _get_matched_keywords(article.title, article.digest)

            channel = db.query(Channel).filter(Channel.id == article.channel_id).first()
            results.append({
                "id": article.id,
                "title": article.title,
                "digest": article.digest,
                "link": article.link,
                "read_num": article.read_num or 0,
                "create_time": article.create_time.strftime("%Y-%m-%d") if article.create_time else "",
                "channel_name": channel.nickname if channel else "未知",
                "channel_id": article.channel_id,
                "matched_keywords": matched_keywords,
            })

        return {
            "success": True,
            "total": len(results),
            "articles": results
        }

    except Exception as e:
        logger.error(f"友商监控中心查询失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.post("/competitor-monitor/detect-all")
async def detect_all_competitor_articles(
    db: Session = Depends(get_db)
):
    """
    重新检测所有文章中的友商合作信息
    返回本次检测到的文章数量
    """
    try:
        articles = db.query(Article).order_by(desc(Article.create_time)).all()

        detected_count = 0
        for article in articles:
            if _detect_competitor_cooperation(article.title, article.digest):
                detected_count += 1

        return {
            "success": True,
            "detected_count": detected_count,
            "total_checked": len(articles),
            "keywords_count": len(COMPETITOR_KEYWORDS)
        }

    except Exception as e:
        logger.error(f"友商检测失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"检测失败: {str(e)}")
