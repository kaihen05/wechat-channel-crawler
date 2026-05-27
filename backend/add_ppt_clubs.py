#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
从PPT中提取的游戏社团，搜索微信公众号并添加到系统
"""
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.database import get_db
from app.models import Channel
from app.services.wechat_crawler import WeChatCrawler
from app.config import settings
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# PPT中的游戏社团（需新增的）
CLUBS_TO_ADD = [
    {"name": "清华大学学生未来游戏技术兴趣团队", "university": "清华大学", "search_kw": ["清华大学未来游戏技术", "清华未来游戏兴趣团队"]},
    {"name": "北大元火动漫社", "university": "北京大学", "search_kw": ["北大元火动漫社", "北大元火"]},
    {"name": "北大学生健康电竞社团", "university": "北京大学", "search_kw": ["北大健康电竞", "北大学生健康电竞"]},
    {"name": "浙江大学临水创制社", "university": "浙江大学", "search_kw": ["浙大临水创制", "浙江大学临水创制社"]},
    {"name": "学生际辉poita动漫美术社", "university": "浙江大学", "search_kw": ["浙大际辉动漫", "浙江大学poita动漫"]},
    {"name": "浙大学生电竞协会", "university": "浙江大学", "search_kw": ["浙大电竞协会", "浙江大学电竞协会"]},
    {"name": "幻圆游戏制作社", "university": "上海交通大学", "search_kw": ["交大幻圆游戏", "上海交大幻圆游戏制作"]},
    {"name": "星丛游戏社", "university": "复旦大学", "search_kw": ["复旦星丛游戏", "星丛游戏社复旦"]},
]


def search_and_add_club(club, crawler, db):
    """搜索一个社团的公众号并添加"""
    name = club["name"]
    university = club["university"]
    
    # 检查是否已存在（按名称模糊匹配）
    existing = db.query(Channel).filter(Channel.nickname.contains(name[:4])).first()
    if existing:
        logger.info(f"  已存在: {existing.nickname} (id={existing.id})")
        return None
    
    # 尝试多个搜索关键词
    for kw in club["search_kw"]:
        logger.info(f"  搜索: {kw}")
        try:
            results = crawler.search_accounts(kw, limit=5)
            if not results:
                logger.info(f"    无结果")
                continue
            
            for r in results:
                nickname = r.get("nickname", "")
                fakeid = r.get("fakeid", "")
                logger.info(f"    找到: {nickname} (fakeid={fakeid})")
                
                # 检查fakeid是否已存在
                dup = db.query(Channel).filter(Channel.fakeid == fakeid).first()
                if dup:
                    logger.info(f"    fakeid已存在: {dup.nickname}")
                    continue
                
                # 创建新频道
                channel = Channel(
                    fakeid=fakeid,
                    nickname=nickname,
                    account_name=r.get("account_name"),
                    avatar_url=r.get("round_head_img"),
                    university_name=university,
                    category="游戏",
                    is_active=True
                )
                db.add(channel)
                db.commit()
                db.refresh(channel)
                logger.info(f"    ✓ 已添加: {nickname} (id={channel.id})")
                return channel
            
            time.sleep(12)
        except Exception as e:
            logger.error(f"    搜索失败: {e}")
    
    logger.warning(f"  ✗ 未找到: {name}")
    return None


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', help='只预览不添加')
    args = parser.parse_args()
    
    crawler = WeChatCrawler(token=settings.wechat_token, cookie=settings.wechat_cookie)
    db = next(get_db())
    
    added = 0
    skipped = 0
    not_found = 0
    
    for club in CLUBS_TO_ADD:
        logger.info(f"\n{'='*50}")
        logger.info(f"处理: {club['name']} ({club['university']})")
        
        if args.dry_run:
            logger.info(f"  [DRY RUN] 将搜索: {club['search_kw']}")
            skipped += 1
            continue
        
        result = search_and_add_club(club, crawler, db)
        if result:
            added += 1
        elif result is None:
            # Check if it was already existing
            existing = db.query(Channel).filter(Channel.nickname.contains(club["name"][:4])).first()
            if existing:
                skipped += 1
            else:
                not_found += 1
        
        time.sleep(12)
    
    logger.info(f"\n{'='*50}")
    logger.info(f"完成！添加: {added}, 已存在: {skipped}, 未找到: {not_found}")
    
    # 显示所有游戏社团
    channels = db.query(Channel).filter(Channel.category == '游戏').all()
    logger.info(f"\n当前所有游戏社团 ({len(channels)} 个):")
    for c in channels:
        logger.info(f"  {c.university_name} | {c.nickname}")
    
    db.close()


if __name__ == "__main__":
    main()
