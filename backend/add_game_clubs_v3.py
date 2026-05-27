#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动添加高校游戏社团到系统 V3

核心原则：只添加名称中明确包含游戏/电竞/桌游等关键词的公众号
不会添加名字仅含"社"但非游戏相关的公众号

标签分类规则：
- 电竞：包含"电竞"、"电子竞技"
- 桌游：包含"桌游"
- 游戏：包含"游戏"、"Minecraft"等游戏名
"""

import sys
import os
import time

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

# 高校简称映射
UNIVERSITY_ALIASES = {
    "上海交通大学": ["上交", "上海交大", "交大", "SJTU"],
    "浙江大学": ["浙大", "ZJU"],
    "复旦大学": ["复旦", "FDU"],
    "北京大学": ["北大", "PKU"],
    "哈尔滨工业大学": ["哈工大", "HIT"],
    "清华大学": ["清华", "THU"],
    "中国科学院大学": ["国科大", "UCAS"],
    "南京大学": ["南大", "NJU"],
    "中国科学技术大学": ["中科大", "USTC", "科大"],
    "西安交通大学": ["西安交大", "西交", "XJTU"],
    "北京大学（深圳）": ["北大深圳", "北大深"],
    "哈尔滨工业大学（深圳）": ["哈工大深圳", "哈工大深"],
    "清华大学（深圳）": ["清华深圳", "清华深"]
}

# 搜索关键词模板 - 多角度搜索
SEARCH_QUERIES = [
    "{uni} 电竞",
    "{uni} 游戏社",
    "{uni} 桌游",
    "{uni} 电子竞技",
    "{alias} 电竞",
    "{alias} 游戏",
]

# ====== 核心过滤：必须包含的游戏相关关键词 ======
# 昵称中必须包含以下至少一个关键词，才会被添加
MUST_CONTAIN_KEYWORDS = [
    # 中文
    "游戏", "电竞", "电子竞技", "桌游",
    "次世代", "玩家",
    "手游", "端游", "网游",
    # 英文
    "Game", "Gaming", "Esports", "esports",
    "Minecraft", "minecraft",
    "LOL", "RPG", "MOBA", "FPS",
    "Steam", "switch", "playstation", "xbox",
    # 游戏名
    "王者荣耀", "原神", "我的世界",
]

# 排除关键词
EXCLUDE_KEYWORDS = [
    "医院", "医学院", "招生", "就业", "招聘",
    "校友", "基金会", "图书馆", "出版社",
    "中学", "小学", "幼儿园", "附属",
    "房产", "地产", "保险", "银行", "证券",
    "社会学", "社工", "社会调查", "社会科学",
    "电子系", "微纳电子", "集成电路",  # 电子≠电竞
]


def is_university_related(nickname: str, university: str) -> bool:
    """检查昵称是否与该高校相关"""
    if university in nickname:
        return True
    uni_clean = university.replace("（", "(").replace("）", ")")
    if uni_clean in nickname:
        return True
    for alias in UNIVERSITY_ALIASES.get(university, []):
        if alias in nickname:
            return True
    # 深圳校区
    if "深圳" in university and "深圳" in nickname:
        base = university.replace("（深圳）", "").replace("（深圳）", "")
        if base in nickname:
            return True
    return False


def contains_game_keyword(nickname: str) -> bool:
    """检查昵称是否包含游戏相关关键词（核心过滤条件）"""
    nl = nickname.lower()
    for kw in MUST_CONTAIN_KEYWORDS:
        if kw.lower() in nl:
            return True
    return False


def should_exclude(nickname: str) -> bool:
    """检查是否应该排除"""
    for kw in EXCLUDE_KEYWORDS:
        if kw in nickname:
            return True
    return False


def classify_channel(nickname: str) -> str:
    """根据昵称关键词智能分类标签"""
    nl = nickname.lower()
    # 电竞
    if any(k in nl for k in ["电竞", "电子竞技", "esports"]):
        return "电竞"
    # 桌游
    if "桌游" in nickname:
        return "桌游"
    # 默认游戏
    return "游戏"


def search_game_clubs_for_university(university: str, crawler: WeChatCrawler, db) -> list:
    """为指定高校搜索游戏社团，返回通过过滤的列表"""
    logger.info(f"\n{'='*60}")
    logger.info(f"搜索 {university} 的游戏社团")
    logger.info(f"{'='*60}")

    found_channels = []
    seen_fakeids = set()
    aliases = UNIVERSITY_ALIASES.get(university, [])

    for query_template in SEARCH_QUERIES:
        # 用高校名或简称替换
        if "{alias}" in query_template:
            if not aliases:
                continue
            for alias in aliases[:1]:  # 只用第一个简称
                search_query = query_template.format(uni=university, alias=alias)
                _do_search(search_query, university, crawler, db, found_channels, seen_fakeids)
        else:
            search_query = query_template.format(uni=university, alias=university)
            _do_search(search_query, university, crawler, db, found_channels, seen_fakeids)

    logger.info(f"\n{university} 共找到 {len(found_channels)} 个游戏社团")
    return found_channels


def _do_search(search_query: str, university: str, crawler, db, found_channels, seen_fakeids):
    """执行单次搜索并过滤"""
    logger.info(f"\n搜索: {search_query}")

    try:
        results = crawler.search_accounts(search_query, limit=10)
        if not results:
            logger.info(f"  未找到结果")
            return

        logger.info(f"  微信返回 {len(results)} 个结果")

        for result in results:
            fakeid = result.get("fakeid")
            nickname = result.get("nickname", "")

            if not fakeid or not nickname:
                continue
            if fakeid in seen_fakeids:
                continue
            seen_fakeids.add(fakeid)

            # 检查是否已存在于数据库
            existing = db.query(Channel).filter(Channel.fakeid == fakeid).first()
            if existing:
                logger.info(f"  - {nickname} (已存在)")
                continue

            # ====== 三重过滤 ======
            # 1. 排除明显不相关的
            if should_exclude(nickname):
                logger.info(f"  ✗ {nickname} → 排除(含排除词)")
                continue

            # 2. 核心：必须包含游戏/电竞关键词
            if not contains_game_keyword(nickname):
                logger.info(f"  ✗ {nickname} → 排除(不含游戏关键词)")
                continue

            # 3. 必须与该高校相关
            if not is_university_related(nickname, university):
                logger.info(f"  ✗ {nickname} → 排除(非本校)")
                continue

            # 通过！
            category = classify_channel(nickname)
            found_channels.append({
                "fakeid": fakeid,
                "nickname": nickname,
                "account_name": result.get("account_name", nickname),
                "avatar_url": result.get("round_head_img", ""),
                "university_name": university,
                "category": category,
            })
            logger.info(f"  ✓ {nickname} → [{category}]")

    except Exception as e:
        logger.error(f"搜索失败: {e}")


def add_channels_to_db(channels: list, db) -> int:
    """添加到数据库"""
    added = 0
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
            added += 1
            logger.info(f"  已入库: {ch['nickname']} [{ch['category']}]")
        except Exception as e:
            db.rollback()
            logger.error(f"  入库失败: {ch['nickname']} - {e}")
    return added


def main():
    import argparse
    parser = argparse.ArgumentParser(description='自动添加高校游戏社团 V3')
    parser.add_argument('--dry-run', action='store_true', help='只预览不添加')
    parser.add_argument('--test', action='store_true', help='只测试前3个高校')
    parser.add_argument('--skip', type=int, default=0, help='跳过前N个高校（用于限流后继续）')
    args = parser.parse_args()

    logger.info("=" * 80)
    logger.info("自动添加高校游戏社团 V3（严格过滤版）")
    logger.info("=" * 80)
    if args.dry_run:
        logger.info("【预览模式】")
    if args.test:
        logger.info("【测试模式】前3个高校")

    if not settings.wechat_token or not settings.wechat_cookie:
        logger.error("未配置微信凭证！")
        return

    crawler = WeChatCrawler(token=settings.wechat_token, cookie=settings.wechat_cookie)
    db = next(get_db())

    try:
        target = UNIVERSITIES[:3] if args.test else UNIVERSITIES[args.skip:]
        if args.skip > 0:
            logger.info(f"【跳过前 {args.skip} 个高校】")
        all_found = []
        total_added = 0

        for i, uni in enumerate(target, 1):
            logger.info(f"\n>>> 进度: {i}/{len(target)}")
            try:
                found = search_game_clubs_for_university(uni, crawler, db)
                all_found.extend(found)

                if not args.dry_run and found:
                    added = add_channels_to_db(found, db)
                    total_added += added

                if i < len(target):
                    logger.info(f"等待 15 秒...")
                    time.sleep(15)
            except Exception as e:
                logger.error(f"处理 {uni} 出错: {e}")
                import traceback
                traceback.print_exc()

        # 总结
        logger.info("\n" + "=" * 80)
        logger.info("完成!")
        logger.info("=" * 80)

        if args.dry_run:
            logger.info(f"\n预览结果（共 {len(all_found)} 个）：")
            for ch in all_found:
                logger.info(f"  {ch['university_name']} | {ch['nickname']} | [{ch['category']}]")
        else:
            logger.info(f"\n总计添加 {total_added} 个社团")
            for ch in all_found:
                logger.info(f"  {ch['university_name']} | {ch['nickname']} | [{ch['category']}]")

        # 数据库统计
        total = db.query(Channel).count()
        logger.info(f"\n数据库总公众号数: {total}")
        cats = db.query(Channel.category).distinct().all()
        for (cat,) in cats:
            cnt = db.query(Channel).filter(Channel.category == cat).count()
            logger.info(f"  {cat}: {cnt}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
