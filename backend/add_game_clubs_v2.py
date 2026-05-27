#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动添加高校游戏社团到系统 V2

改进：
1. 使用精确搜索关键词，减少误匹配
2. 智能过滤：验证昵称必须包含游戏/电竞相关词
3. 正确标签分类：根据名称内容自动判断分类
4. 先预览结果再确认添加
5. 修复 avatar_url 字段名（原错误使用 round_head_img）
"""

import sys
import os
import time
import re

# 添加 backend 到路径
sys.path.insert(0, os.path.dirname(__file__))

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

# 高校简称映射（用于匹配）
UNIVERSITY_ALIASES = {
    "上海交通大学": ["上交", "上海交大", "交大", "SJTU"],
    "浙江大学": ["浙大", "ZJU"],
    "复旦大学": ["复旦", "FDU"],
    "北京大学": ["北大", "PKU", "燕园"],
    "哈尔滨工业大学": ["哈工大", "HIT"],
    "清华大学": ["清华", "THU"],
    "中国科学院大学": ["国科大", "UCAS"],
    "南京大学": ["南大", "NJU"],
    "中国科学技术大学": ["中科大", "USTC", "科大"],
    "西安交通大学": ["西安交大", "西交", "XJTU"],
    "北京大学（深圳）": ["北大深圳", "北大深", "PKU深圳"],
    "哈尔滨工业大学（深圳）": ["哈工大深圳", "哈工大深", "HIT深圳"],
    "清华大学（深圳）": ["清华深圳", "清华深", "THU深圳"]
}

# 搜索关键词模板 - 精确搜索
SEARCH_QUERIES = [
    "{uni} 电竞",
    "{uni} 游戏社",
    "{uni} 桌游",
]

# ====== 过滤规则 ======

# 必须包含的关键词（昵称中至少包含一个）
GAME_RELATED_KEYWORDS = [
    "游戏", "电竞", "电子竞技", "桌游", "主机", "switch",
    "playstation", "xbox", "Game", "Gaming", "Esports",
    "次世代", "玩家", "手游", "端游", "网游", "RPG",
    "MOBA", "FPS", "电竞社", "游戏社", "桌游社",
    "LOL", "王者荣耀", "原神", "Steam",
    "Minecraft", "minecraft", "我的世界",
]

# 排除关键词（包含这些的直接排除）
EXCLUDE_KEYWORDS = [
    "医院", "医学院", "招生", "就业", "招聘", "招聘会",
    "校友", "基金会", "图书馆", "出版社", "杂志",
    "中学", "小学", "幼儿园", "附属",
    "房产", "地产", "保险", "银行", "证券",
    "每日电讯", "课堂", "在线教育",
]

# 分类规则：根据昵称关键词判断分类
CATEGORY_RULES = {
    "电竞": ["电竞", "电子竞技", "Esports", "esports", "LOL", "王者荣耀"],
    "游戏": ["游戏", "Game", "game", "gaming", "Gaming", "次世代", "玩家", "手游", "端游", "网游", "RPG", "MOBA", "FPS", "原神", "Steam", "switch", "playstation", "xbox"],
    "桌游": ["桌游", "卡牌", "棋牌"],
    "综合": ["社团", "协会", "联会", "联盟", "俱乐部", "社"],
}


def is_university_related(nickname: str, university: str) -> bool:
    """检查昵称是否与该高校相关"""
    # 直接包含高校全名
    if university.replace("（", "(").replace("）", ")") in nickname:
        return True
    if university in nickname:
        return True

    # 检查简称
    aliases = UNIVERSITY_ALIASES.get(university, [])
    for alias in aliases:
        if alias in nickname:
            return True

    # 深圳校区特殊处理
    if "深圳" in university and "深圳" in nickname:
        # 需要同时匹配学校名
        base_uni = university.replace("（深圳）", "").replace("（深圳）", "")
        if base_uni in nickname:
            return True
        for alias in aliases:
            if alias in nickname:
                return True

    return False


def is_game_related(nickname: str) -> bool:
    """检查昵称是否与游戏/电竞相关"""
    nickname_lower = nickname.lower()
    for keyword in GAME_RELATED_KEYWORDS:
        if keyword.lower() in nickname_lower:
            return True
    return False


def should_exclude(nickname: str) -> bool:
    """检查是否应该排除"""
    for keyword in EXCLUDE_KEYWORDS:
        if keyword in nickname:
            return True
    return False


def classify_channel(nickname: str) -> str:
    """根据昵称智能分类"""
    for category, keywords in CATEGORY_RULES.items():
        for keyword in keywords:
            if keyword.lower() in nickname.lower():
                return category
    return "游戏"  # 默认游戏


def search_game_clubs_for_university(university: str, crawler: WeChatCrawler, db, dry_run=False) -> list:
    """
    为指定高校搜索游戏社团

    返回找到的社团列表（包含分类信息）
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"搜索 {university} 的游戏社团")
    logger.info(f"{'='*60}")

    found_channels = []
    seen_fakeids = set()

    for query_template in SEARCH_QUERIES:
        search_query = query_template.format(uni=university)
        logger.info(f"\n搜索关键词: {search_query}")

        try:
            results = crawler.search_accounts(search_query, limit=10)

            if not results:
                logger.info(f"  未找到结果")
                continue

            logger.info(f"  微信返回 {len(results)} 个结果")

            for result in results:
                fakeid = result.get("fakeid")
                nickname = result.get("nickname", "")

                if not fakeid or not nickname:
                    continue

                # 去重
                if fakeid in seen_fakeids:
                    continue
                seen_fakeids.add(fakeid)

                # 检查是否已存在于数据库
                existing = db.query(Channel).filter(Channel.fakeid == fakeid).first()
                if existing:
                    logger.info(f"  - {nickname} (已存在于数据库)")
                    continue

                # ====== 过滤逻辑 ======

                # 1. 排除明显不相关的
                if should_exclude(nickname):
                    logger.info(f"  ✗ {nickname} (排除: 包含排除关键词)")
                    continue

                # 2. 必须与游戏/电竞相关
                #    或者包含高校名+"社"（如"XX大学Minecraft社"）
                is_game = is_game_related(nickname)
                is_uni_club = is_university_related(nickname, university) and (
                    "社" in nickname or "协会" in nickname or "联盟" in nickname or "俱乐部" in nickname
                )
                if not is_game and not is_uni_club:
                    logger.info(f"  ✗ {nickname} (排除: 非游戏相关)")
                    continue

                # 3. 必须与该高校相关
                if not is_university_related(nickname, university):
                    logger.info(f"  ✗ {nickname} (排除: 非本校相关)")
                    continue

                # ====== 通过过滤 ======
                category = classify_channel(nickname)
                # 如果关键词分类为空但通过了高校+社匹配，默认标记为"游戏"
                if category == "游戏" and not is_game_related(nickname):
                    category = "游戏"  # 通过游戏搜索找到的高校社团，默认游戏分类
                account_name = result.get("account_name", nickname)

                found_channels.append({
                    "fakeid": fakeid,
                    "nickname": nickname,
                    "account_name": account_name,
                    "avatar_url": result.get("round_head_img", ""),
                    "university_name": university,
                    "category": category,
                })

                logger.info(f"  ✓ {nickname} → 分类: {category}")

        except Exception as e:
            logger.error(f"搜索 '{search_query}' 失败: {e}")
            continue

    logger.info(f"\n{university} 共找到 {len(found_channels)} 个游戏社团")
    return found_channels


def add_channels_to_db(channels: list, db) -> int:
    """将筛选后的社团添加到数据库"""
    added_count = 0
    for ch in channels:
        try:
            channel = Channel(
                fakeid=ch["fakeid"],
                nickname=ch["nickname"],
                account_name=ch["account_name"],
                avatar_url=ch["avatar_url"],
                university_name=ch["university_name"],
                category=ch["category"],
                is_active=True
            )
            db.add(channel)
            db.commit()
            added_count += 1
            logger.info(f"  已添加: {ch['nickname']} (分类: {ch['category']})")
        except Exception as e:
            db.rollback()
            logger.error(f"  添加失败 {ch['nickname']}: {e}")
    return added_count


def main():
    """主函数"""
    import argparse
    parser = argparse.ArgumentParser(description='自动添加高校游戏社团 V2')
    parser.add_argument('--dry-run', action='store_true', help='只预览结果，不实际添加')
    parser.add_argument('--test', action='store_true', help='只测试前2个高校')
    args = parser.parse_args()

    logger.info("=" * 80)
    logger.info("自动添加高校游戏社团 V2（精确过滤版）")
    logger.info("=" * 80)

    if args.dry_run:
        logger.info("【预览模式】不会实际添加数据")
    if args.test:
        logger.info("【测试模式】只处理前2个高校")

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
        target_unis = UNIVERSITIES[:2] if args.test else UNIVERSITIES
        all_found = []
        total_added = 0

        for i, university in enumerate(target_unis, 1):
            logger.info(f"\n进度: {i}/{len(target_unis)}")

            try:
                found = search_game_clubs_for_university(
                    university, crawler, db, dry_run=args.dry_run
                )
                all_found.extend(found)

                if not args.dry_run and found:
                    added = add_channels_to_db(found, db)
                    total_added += added

                # 高校间延迟
                if i < len(target_unis):
                    delay_time = 12
                    logger.info(f"等待 {delay_time} 秒后继续...")
                    time.sleep(delay_time)

            except Exception as e:
                logger.error(f"处理 {university} 时出错: {e}")
                import traceback
                traceback.print_exc()
                continue

        # ====== 输出总结 ======
        logger.info("\n" + "=" * 80)
        logger.info("执行完成")
        logger.info("=" * 80)

        if args.dry_run:
            logger.info(f"\n【预览模式】共找到 {len(all_found)} 个符合条件的社团：")
            for ch in all_found:
                logger.info(f"  {ch['university_name']} | {ch['nickname']} | 分类: {ch['category']}")
        else:
            logger.info(f"\n总计添加 {total_added} 个游戏社团")

            # 按高校和分类统计
            if all_found:
                logger.info(f"\n添加详情：")
                for ch in all_found:
                    logger.info(f"  {ch['university_name']} | {ch['nickname']} | {ch['category']}")

        # 统计数据库
        total_channels = db.query(Channel).count()
        logger.info(f"\n数据库总公众号数: {total_channels}")

        # 按分类统计
        categories = db.query(Channel.category).distinct().all()
        for (cat,) in categories:
            count = db.query(Channel).filter(Channel.category == cat).count()
            logger.info(f"  {cat}: {count} 个")

    finally:
        db.close()


if __name__ == "__main__":
    main()
