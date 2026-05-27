#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import logging
logging.basicConfig(level=logging.DEBUG)
from app.services.wechat_crawler import WeChatCrawler
from app.config import settings

crawler = WeChatCrawler(token=settings.wechat_token, cookie=settings.wechat_cookie)
# 北大熊电竞
result = crawler.get_articles(fakeid='MzYzMzE4NDMxNg==', days=90, count=10)
print('Articles found:', len(result))
for a in result:
    t = a.get('title', '?')
    print(' ', t[:50])
