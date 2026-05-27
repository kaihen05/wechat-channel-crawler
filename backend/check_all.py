import sys
sys.path.insert(0, 'C:/Users/kaiboy/Desktop/wechat-channel-crawler/backend')

from app.database import SessionLocal
from app.models import Article, Channel

db = SessionLocal()
try:
    # 检查所有公众号和它们的累计阅读量
    channels = db.query(Channel).all()
    print("所有公众号的累计阅读量:")
    print("=" * 80)
    for channel in channels:
        # 计算实际总阅读量
        from sqlalchemy import func
        actual_total = db.query(func.sum(Article.read_num)).filter(
            Article.channel_id == channel.id
        ).scalar() or 0
        print(f"ID: {channel.id}, 名称: {channel.nickname}, 数据库={channel.total_read_num}, 实际计算={actual_total}")

    # 检查测试技术公众号的文章
    print("\n测试技术公众号（ID=2）的文章:")
    print("=" * 80)
    tech_articles = db.query(Article).filter(Article.channel_id == 2).all()
    for article in tech_articles:
        print(f"文章 ID: {article.id}, 标题: {article.title}, 阅读: {article.read_num}")
finally:
    db.close()
