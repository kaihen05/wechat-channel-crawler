#!/usr/bin/env python
"""
手动测试文章API逻辑
这个脚本独立于FastAPI服务器运行，直接测试逻辑
"""
import sys
sys.path.insert(0, 'C:/Users/kaiboy/Desktop/wechat-channel-crawler/backend')

from app.database import SessionLocal
from app.models import Article
from sqlalchemy import desc
import json

def test_article_api():
    """测试文章API逻辑"""
    db = SessionLocal()
    try:
        # 获取前3篇文章
        articles = db.query(Article).order_by(desc(Article.create_time)).limit(3).all()

        # 转换为响应格式（与API完全相同的逻辑）
        result = []
        for article in articles:
            article_dict = {
                "id": article.id,
                "channel_id": article.channel_id,
                "title": article.title,
                "link": article.link,
                "author": article.author or "未知作者",
                "create_time": article.create_time.isoformat() if article.create_time else None,
                "collected_at": article.collected_at.isoformat() if article.collected_at else None,
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

        print("=" * 80)
        print("文章API测试结果")
        print("=" * 80)
        for i, article in enumerate(result, 1):
            print(f"\n文章 {i}:")
            print(f"  ID: {article['id']}")
            print(f"  标题: {article['title']}")
            print(f"  公众号: {article['channel_name']}")
            print(f"  文章阅读量: {article['read_num']}")
            print(f"  公众号累计阅读量: {article['channel_total_read_num']}")
            print(f"  所有字段: {list(article.keys())}")

        print("\n" + "=" * 80)
        print("总结:")
        print("=" * 80)
        print(f"总文章数: {len(result)}")
        print(f"包含 channel_total_read_num 字段的文章数: {sum(1 for a in result if a['channel_total_read_num'] is not None)}")

        # 检查是否有文章有非零的累计阅读量
        non_zero = [a for a in result if a['channel_total_read_num'] > 0]
        if non_zero:
            print(f"\n有非零累计阅读量的公众号:")
            for a in non_zero:
                print(f"  {a['channel_name']}: {a['channel_total_read_num']}")
        else:
            print("\n注意: 所有文章的公众号累计阅读量都是0，这意味着:")
            print("  1. 这些公众号的文章都没有阅读量")
            print("  2. 或者数据库中的 total_read_num 字段是0")
            print("\n要查看有数据的公众号，请在数据库中查询 '测试技术公众号'（ID=2）")

        return result

    finally:
        db.close()

if __name__ == "__main__":
    test_article_api()
