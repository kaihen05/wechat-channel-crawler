"""
Sync articles for newly added product and tech clubs.
"""
import sys, os, time
sys.path.insert(0, os.path.dirname('.'))
from app.database import get_db
from app.models import Channel, Article
from app.services.wechat_crawler import WeChatCrawler
from app.config import settings
from sqlalchemy import func

crawler = WeChatCrawler(token=settings.wechat_token, cookie=settings.wechat_cookie)
db = next(get_db())

# Get channels with no articles
channels = db.query(Channel).filter(Channel.category.in_(['产品', '技术'])).all()
no_article_channels = []
for c in channels:
    art_count = db.query(Article).filter(Article.channel_id == c.id).count()
    if art_count == 0:
        no_article_channels.append(c)

print(f'Channels needing sync: {len(no_article_channels)}')

for channel in no_article_channels:
    print(f'\n--- Syncing: {channel.nickname} (fakeid={channel.fakeid}) ---')
    try:
        articles = crawler.get_articles(fakeid=channel.fakeid, days=90, count=10)
        print(f'  Got {len(articles)} articles from API')
        
        count = 0
        for article_data in articles:
            content_url = article_data.get('content_url')
            if not content_url:
                continue
            existing = db.query(Article).filter(Article.content_url == content_url).first()
            if existing:
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
            title = article_data.get('title', '?')
            print(f'  Added: {title[:50]}')
        
        total_reads = db.query(Article).filter(Article.channel_id == channel.id).with_entities(func.sum(Article.read_num)).scalar() or 0
        channel.total_read_num = total_reads
        db.commit()
        print(f'  ✅ {channel.nickname}: {count} articles added')
    except Exception as e:
        print(f'  ❌ Error: {e}')
        db.rollback()
    
    time.sleep(5)

# Final summary
print(f'\n===== Final Summary =====')
for cat in ['产品', '技术']:
    channels = db.query(Channel).filter(Channel.category == cat).all()
    print(f'\n=== {cat} ({len(channels)}) ===')
    for c in channels:
        art_count = db.query(Article).filter(Article.channel_id == c.id).count()
        print(f'  {c.university_name} | {c.nickname} | {art_count} articles')

db.close()
