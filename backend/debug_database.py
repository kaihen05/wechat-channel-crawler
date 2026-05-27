import sys
sys.path.insert(0, 'C:/Users/kaiboy/Desktop/wechat-channel-crawler/backend')

from app.database import SessionLocal
from app.models import Article, Channel

db = SessionLocal()
try:
    # 获取一篇文章
    article = db.query(Article).first()
    if article:
        print(f"文章 ID: {article.id}")
        print(f"文章标题: {article.title}")
        print(f"Channel ID: {article.channel_id}")
        print(f"Channel 对象: {article.channel}")
        print(f"Channel nickname: {article.channel.nickname}")
        print(f"Channel total_read_num: {article.channel.total_read_num}")
        print(f"Channel 有 total_read_num 属性: {hasattr(article.channel, 'total_read_num')}")
        print(f"Channel 类型: {type(article.channel)}")
        print(f"Channel 所有属性: {[attr for attr in dir(article.channel) if not attr.startswith('_')]}")
    else:
        print("没有文章")
finally:
    db.close()
