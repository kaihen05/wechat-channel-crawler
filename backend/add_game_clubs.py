#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动添加高校游戏社团到系统

功能：
1. 根据高校名称自动搜索相关的游戏社团公众号
2. 将找到的社团添加到系统中
3. 分类标记为"游戏"
"""

import sys
import os
import time

# 添加 backend 到路径
sys.path.insert(0, os.path.dirname(__file__))

from app.database import get_db
from app.models import Channel
from app.services.wechat_crawler import WeChatCrawler
from app.config import settings
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 高校列表
UNIVERSITIES = [
    "上海交通大学",
    "浙江大学",
    "复旦大学",
    "北京大学",
    "哈尔滨工业大学",
    "清华大学",
    "中国科学院大学",
    "南京大学",
    "中国科学技术大学",
    "西安交通大学",
    "北京大学（深圳）",
    "哈尔滨工业大学（深圳）",
    "清华大学（深圳）"
]

# 游戏相关关键词
GAME_KEYWORDS = [
    "游戏",
    "电竞",
    "电子竞技",
    "game",
    "esports",
    "桌游",
    "卡牌",
    "主机",
    "switch",
    "playstation",
    "xbox"
]

def search_game_clubs_for_university(university: str, crawler: WeChatCrawler, db) -> int:
    """
    为指定高校搜索游戏社团

    返回添加的社团数量
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"开始搜索 {university} 的游戏社团")
    logger.info(f"{'='*60}")

    total_added = 0

    # 使用多个关键词搜索
    for keyword in GAME_KEYWORDS:
        search_query = f"{university} {keyword}"
        logger.info(f"\n搜索关键词: {search_query}")

        try:
            # 搜索公众号
            results = crawler.search_accounts(search_query, limit=10)

            if not results:
                logger.info(f"  未找到结果")
                continue

            logger.info(f"  找到 {len(results)} 个结果")

            # 过滤并添加社团
            for result in results:
                fakeid = result.get("fakeid")
                nickname = result.get("nickname", "")
                account_name = result.get("account_name", nickname)

                if not fakeid or not nickname:
                    continue

                # 检查是否已存在
                existing = db.query(Channel).filter(
                    Channel.fakeid == fakeid
                ).first()

                if existing:
                    logger.info(f"  - {nickname} (已存在)")
                    continue

                # 添加新社团
                channel = Channel(
                    fakeid=fakeid,
                    nickname=nickname,
                    account_name=account_name,
                    avatar_url=result.get("round_head_img"),
                    university_name=university,
                    category="游戏",
                    is_active=True
                )
                db.add(channel)
                db.commit()
                total_added += 1
                logger.info(f"  ✓ 添加: {nickname}")

            # 搜索后延迟
            time.sleep(3)

        except Exception as e:
            logger.error(f"搜索 '{search_query}' 失败: {e}")
            continue

    logger.info(f"\n{university} 添加完成，共添加 {total_added} 个社团")
    return total_added

def main():
    """主函数"""
    logger.info("="*80)
    logger.info("开始自动添加高校游戏社团")
    logger.info("="*80)

    # 检查凭证
    if not settings.wechat_token or not settings.wechat_cookie:
        logger.error("未配置微信凭证！请在 .env 文件中设置 WECHAT_TOKEN 和 WECHAT_COOKIE")
        return

    # 创建爬虫实例
    crawler = WeChatCrawler(
        token=settings.wechat_token,
        cookie=settings.wechat_cookie
    )

    # 获取数据库连接
    db = next(get_db())

    try:
        total_added = 0
        success_universities = []

        # 遍历所有高校
        for university in UNIVERSITIES:
            try:
                added_count = search_game_clubs_for_university(
                    university,
                    crawler,
                    db
                )
                total_added += added_count

                if added_count > 0:
                    success_universities.append(f"{university} ({added_count}个)")

                # 高校间延迟，避免请求过快
                time.sleep(5)

            except Exception as e:
                logger.error(f"处理 {university} 时出错: {e}")
                continue

        # 输出总结
        logger.info("\n" + "="*80)
        logger.info("执行完成")
        logger.info("="*80)
        logger.info(f"\n总计添加 {total_added} 个游戏社团")
        logger.info(f"\n成功的高校 ({len(success_universities)}):")
        for uni_info in success_universities:
            logger.info(f"  - {uni_info}")

        # 统计数据库中的社团总数
        total_channels = db.query(Channel).count()
        game_channels = db.query(Channel).filter(
            Channel.category == "游戏"
        ).count()
        logger.info(f"\n当前系统概况:")
        logger.info(f"  - 总公众号数: {total_channels}")
        logger.info(f"  - 游戏社团数: {game_channels}")

    finally:
        db.close()

if __name__ == "__main__":
    main()
