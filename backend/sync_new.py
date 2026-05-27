#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Sync articles for newly added channels"""
import sys, os, time
sys.path.insert(0, os.path.dirname(__file__))
from app.database import get_db
from app.models import Channel, Article
from app.services.wechat_crawler import WeChatCrawler
from app.config import settings
from sqlalchemy import func

db = next(get_db())
crawler = WeChatCrawler(token=settings.wechat_token, cookie=settings.wechat_cookie)

# Find channels without articles
channels = db.query(Channel).filter(Channel.category == '游戏').all()
no_article = []
for c in channels:
    count = db.query(Article).filter(Article.channel_id == c.id).count()
    if count == 0:
        no_article.append(c)

print(f'Channels without articles: {len(no_article)}')
for c in no_article:
    print(f'  {c.nickname} (fakeid={c.fakeid})')

for channel in no_article:
    print(f'\nSyncing: {channel.nickname}')
    try:
        articles = crawler.get_articles(fakeid=channel.fakeid, days=30, count=10)
        print(f'  Got {len(articles)} articles')
        
        added = 0
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
            added += 1
        
        total_reads = db.query(Article).filter(
            Article.channel_id == channel.id
        ).with_entities(func.sum(Article.read_num)).scalar() or 0
        channel.total_read_num = total_reads
        
        db.commit()
        print(f'  Added {added} articles')
    except Exception as e:
        print(f'  Error: {e}')
        db.rollback()
    
    time.sleep(12)

db.close()
print('\nDone!')
