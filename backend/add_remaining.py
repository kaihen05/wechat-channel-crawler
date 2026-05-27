#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os, time
sys.path.insert(0, os.path.dirname(__file__))
from app.database import get_db
from app.models import Channel
from app.services.wechat_crawler import WeChatCrawler
from app.config import settings

crawler = WeChatCrawler(token=settings.wechat_token, cookie=settings.wechat_cookie)
db = next(get_db())

# Add "未来动漫游戏技术兴趣团队" for Tsinghua
results = crawler.search_accounts('清华游戏技术兴趣团队', limit=5)
for r in results:
    nickname = r.get('nickname', '')
    fakeid = r.get('fakeid', '')
    if '游戏' in nickname and '兴趣' in nickname:
        dup = db.query(Channel).filter(Channel.fakeid == fakeid).first()
        if dup:
            print(f'Already exists: {dup.nickname}')
            break
        channel = Channel(
            fakeid=fakeid,
            nickname=nickname,
            account_name=r.get('account_name'),
            avatar_url=r.get('round_head_img'),
            university_name='清华大学',
            category='游戏',
            is_active=True
        )
        db.add(channel)
        db.commit()
        db.refresh(channel)
        print(f'Added: {nickname} (id={channel.id})')
        break

db.close()
