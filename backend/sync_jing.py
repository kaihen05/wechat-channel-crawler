import sys, os
sys.path.insert(0, os.path.dirname('.'))
from app.database import get_db
from app.models import Channel, Article
from app.services.wechat_crawler import WeChatCrawler
from app.config import settings
from sqlalchemy import func

crawler = WeChatCrawler(token=settings.wechat_token, cookie=settings.wechat_cookie)
db = next(get_db())

channel = db.query(Channel).filter(Channel.id == 40).first()
print(f'Syncing: {channel.nickname} (fakeid={channel.fakeid})')

try:
    articles = crawler.get_articles(fakeid=channel.fakeid, days=90, count=10)
    print(f'Got {len(articles)} articles from API')
    
    count = 0
    for article_data in articles:
        content_url = article_data.get('content_url')
        if not content_url:
            continue
        existing = db.query(Article).filter(Article.content_url == content_url).first()
        if existing:
            print(f'  Skip: {article_data.get("title", "?")[:40]}')
            continue
        article = Article(
            channel_id=channel.id,
            title=article_data.get('title', ''),
            content_url=content_url,
            link=article_data.get('link', ''),
            digest=article_data.get('digest'),
            author=article_data.get('author'),
            cover_url=article_data.get('cover'),
            create_time=article_data.get('create_time'),
            read_num=article_data.get('read_num', 0),
            msgid=article_data.get('msgid', '')
        )
        db.add(article)
        count += 1
        print(f'  Added: {article_data.get("title", "?")[:40]}')
    
    total_reads = db.query(Article).filter(Article.channel_id == channel.id).with_entities(func.sum(Article.read_num)).scalar() or 0
    channel.total_read_num = total_reads
    db.commit()
    print(f'Done! Added {count} articles for {channel.nickname}')
except Exception as e:
    print(f'Error: {e}')
    db.rollback()

db.close()
