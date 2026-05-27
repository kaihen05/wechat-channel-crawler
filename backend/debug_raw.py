#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import httpx
import json
from app.config import settings

url = "https://mp.weixin.qq.com/cgi-bin/appmsg"
params = {
    "action": "list_ex",
    "begin": 0,
    "count": 10,
    "fakeid": "MzYzMzE4NDMxNg==",
    "type": 9,
    "query": "",
    "token": settings.wechat_token,
    "lang": "zh_CN",
    "f": "json",
    "ajax": 1
}
headers = {
    "Cookie": settings.wechat_cookie,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

with httpx.Client(timeout=30.0, follow_redirects=True) as client:
    response = client.get(url, headers=headers, params=params)
    print("Status:", response.status_code)
    data = response.json()
    print("Response:", json.dumps(data, ensure_ascii=False, indent=2))

# Also try a known-working channel (THU紫荆电竞 fakeid=Mzk0NTY4NTg5MA==)
print("\n--- Trying THU紫荆电竞 ---")
params2 = params.copy()
params2["fakeid"] = "Mzk0NTY4NTg5MA=="
with httpx.Client(timeout=30.0, follow_redirects=True) as client:
    response2 = client.get(url, headers=headers, params=params2)
    data2 = response2.json()
    print("Status:", response2.status_code)
    # Just show keys and article count
    print("Keys:", list(data2.keys()))
    app_msg_list = data2.get("app_msg_list", [])
    print("Articles count:", len(app_msg_list))
    if app_msg_list:
        print("First article:", app_msg_list[0].get("title", "?")[:50])
