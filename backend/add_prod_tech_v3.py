"""
Second round: search for clubs that didn't match well in first round.
"""
import sys, os, time
sys.path.insert(0, os.path.dirname('.'))
from app.services.wechat_crawler import WeChatCrawler
from app.config import settings

crawler = WeChatCrawler(token=settings.wechat_token, cookie=settings.wechat_cookie)

# Clubs that need more specific searches
searches = [
    # 清华互联网产品研究协会 - try more specific
    ("清华互联网产品研究协会", "清华产品研究协会"),
    ("清华产品经理协会", "清华产品协会"),
    # 浙大学生互联网协会
    ("浙大学生互联网协会", "浙江大学互联网协会"),
    # 清华算法协会
    ("清华大学算法协会", "清华THUALGO"),
    # 清华超算
    ("清华超算队", "清华学生超算"),
    # 清华通用人工智能协会
    ("清华通用人工智能协会", "THUAGI"),
    # 清华人工智能治理协会
    ("清华学生人工智能治理", "TAIGA清华"),
    # 清华大数据
    ("数据派THU", "清华大数据协会"),
    # 北大人工智能创新协会
    ("北大AIIA", "北大人工智能创新协会"),
    # 北大超算队
    ("北大超算队", "PKUHPC"),
    # 北大Linus俱乐部
    ("北大Linus俱乐部", "北大Linux俱乐部"),
    # 北大算法协会
    ("北大算法协会", "PKUSAA"),
    # 浙大AI俱乐部
    ("浙大人工智能俱乐部", "ZJUAI"),
    # 浙大超算
    ("浙大超算队", "ZJUSCT"),
    # 交大AI创新协会
    ("SJTUAIIA", "交大人工智能创新协会"),
    # 思源极客
    ("思源极客", "SJTU思源极客"),
    # 复旦信息网络安全
    ("复旦信息网络安全协会", "FDUNSS"),
    # sixstars
    ("sixstars复旦", "复旦sixstars"),
]

for label, q in searches:
    print(f'\n=== {label}: "{q}" ===')
    results = crawler.search_accounts(q, limit=3)
    if not results:
        print('    ❌ No results')
    else:
        for r in results:
            nickname = r.get('nickname', '')
            fakeid = r.get('fakeid', '')
            sig = r.get('signature', '')[:60] if r.get('signature') else ''
            print(f'    📱 {nickname} | fakeid={fakeid} | {sig}')
    time.sleep(12)
