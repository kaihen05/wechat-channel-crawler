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

# 1. Search for Tsinghua future game team
queries = ['清华未来游戏', '清华游戏技术兴趣团队', '清华大学游戏兴趣团队', '清华未来游戏技术', '北大健康电竞']
for q in queries:
    print(f'Search: {q}')
    results = crawler.search_accounts(q, limit=5)
    if results:
        for r in results:
            nickname = r.get('nickname', '')
            fakeid = r.get('fakeid', '')
            dup = db.query(Channel).filter(Channel.fakeid == fakeid).first()
            status = 'DUP' if dup else 'NEW'
            print(f'  {nickname} ({status})')
    else:
        print(f'  No results')
    time.sleep(12)

db.close()
