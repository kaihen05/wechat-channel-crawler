#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
精确搜索PPT中剩余的游戏社团 - 带验证
"""
import sys
import os
import time
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.database import get_db
from app.models import Channel
from app.services.wechat_crawler import WeChatCrawler
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Remaining clubs to add with multiple search keywords and validation
CLUBS = [
    {
        "target_name": "清华大学学生未来游戏技术兴趣团队",
        "university": "清华大学",
        "keywords": ["清华大学未来游戏", "清华未来游戏兴趣团队", "清华游戏技术兴趣团队"],
        "validate": lambda n: ("游戏" in n or "未来" in n) and ("清华" in n or "THU" in n.upper())
    },
    {
        "target_name": "北大学生健康电竞社团",
        "university": "北京大学",
        "keywords": ["北大学生健康电竞", "北大健康电竞社团", "北大电竞社团"],
        "validate": lambda n: "电竞" in n and ("北大" in n or "北京" in n)
    },
    {
        "target_name": "浙大学生电竞协会",
        "university": "浙江大学",
        "keywords": ["浙江大学电竞协会", "浙大学生电竞协会", "浙大电竞"],
        "validate": lambda n: "电竞" in n and ("浙" in n or "ZJU" in n.upper())
    },
    {
        "target_name": "幻圆游戏制作社",
        "university": "上海交通大学",
        "keywords": ["幻圆游戏", "交大幻圆", "上海交大幻圆游戏制作社"],
        "validate": lambda n: "幻圆" in n or ("游戏" in n and "制作" in n)
    },
    {
        "target_name": "星丛游戏社",
        "university": "复旦大学",
        "keywords": ["星丛游戏社", "复旦星丛", "复旦大学星丛"],
        "validate": lambda n: "星丛" in n
    },
]


def main():
    crawler = WeChatCrawler(token=settings.wechat_token, cookie=settings.wechat_cookie)
    db = next(get_db())
    
    added = 0
    not_found = 0
    
    for club in CLUBS:
        logger.info(f"\n{'='*50}")
        logger.info(f"搜索: {club['target_name']} ({club['university']})")
        
        # Check if already exists
        existing = db.query(Channel).filter(
            Channel.university_name == club["university"],
            Channel.nickname.contains(club["target_name"][:3])
        ).first()
        if existing:
            logger.info(f"  已存在: {existing.nickname}")
            continue
        
        found = False
        for kw in club["keywords"]:
            if found:
                break
            logger.info(f"  关键词: {kw}")
            try:
                results = crawler.search_accounts(kw, limit=10)
                if not results:
                    logger.info(f"    无结果")
                    continue
                
                for r in results:
                    nickname = r.get("nickname", "")
                    fakeid = r.get("fakeid", "")
                    logger.info(f"    候选: {nickname}")
                    
                    # Validate
                    if not club["validate"](nickname):
                        logger.info(f"      验证失败 - 不匹配")
                        continue
                    
                    # Check duplicate
                    dup = db.query(Channel).filter(Channel.fakeid == fakeid).first()
                    if dup:
                        logger.info(f"      fakeid已存在: {dup.nickname}")
                        continue
                    
                    # Add
                    channel = Channel(
                        fakeid=fakeid,
                        nickname=nickname,
                        account_name=r.get("account_name"),
                        avatar_url=r.get("round_head_img"),
                        university_name=club["university"],
                        category="游戏",
                        is_active=True
                    )
                    db.add(channel)
                    db.commit()
                    db.refresh(channel)
                    logger.info(f"      ✓ 已添加: {nickname} (id={channel.id})")
                    added += 1
                    found = True
                    break
                
                time.sleep(12)
            except Exception as e:
                logger.error(f"    搜索失败: {e}")
        
        if not found:
            logger.warning(f"  ✗ 未找到匹配的公众号: {club['target_name']}")
            not_found += 1
    
    # Show all game channels
    channels = db.query(Channel).filter(Channel.category == '游戏').all()
    logger.info(f"\n当前所有游戏社团 ({len(channels)} 个):")
    for c in channels:
        logger.info(f"  {c.university_name} | {c.nickname}")
    
    logger.info(f"\n完成！添加: {added}, 未找到: {not_found}")
    db.close()


if __name__ == "__main__":
    main()
