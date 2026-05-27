"""
Add product and tech clubs with verified search results.
Uses manual search + confirmation approach.
"""
import sys, os, time
sys.path.insert(0, os.path.dirname('.'))
from app.database import get_db
from app.models import Channel, Article
from app.services.wechat_crawler import WeChatCrawler
from app.config import settings

def search_club(crawler, query, limit=3):
    """Search and display results for manual review."""
    print(f'\n  Searching: "{query}"')
    results = crawler.search_accounts(query, limit=limit)
    if not results:
        print('    ❌ No results')
        return None
    for r in results:
        nickname = r.get('nickname', '')
        fakeid = r.get('fakeid', '')
        sig = r.get('signature', '')[:60] if r.get('signature') else ''
        print(f'    📱 {nickname} | fakeid={fakeid} | {sig}')
    return results

def add_channel(db, university, category, nickname, fakeid, avatar_url=''):
    """Add a channel to database."""
    dup = db.query(Channel).filter(Channel.fakeid == fakeid).first()
    if dup:
        print(f'    ⚠️ Duplicate: {dup.nickname} (id={dup.id})')
        return dup
    channel = Channel(
        fakeid=fakeid,
        nickname=nickname,
        avatar_url=avatar_url,
        university_name=university,
        category=category,
        is_active=True
    )
    db.add(channel)
    db.commit()
    db.refresh(channel)
    print(f'    ✅ Added: {nickname} -> {university} [{category}]')
    return channel

def main():
    crawler = WeChatCrawler(token=settings.wechat_token, cookie=settings.wechat_cookie)
    db = next(get_db())
    
    # ==========================================
    # STEP 1: Search all clubs to find matches
    # ==========================================
    
    search_list = [
        # 产品
        ("清华大学", "产品", ["清华互联网产品", "清华产品研究协会"]),
        ("清华大学", "产品", ["AttraX"]),
        ("北京大学", "产品", ["清华互联网产品"]),  # Same as THU per PPT
        ("浙江大学", "产品", ["弦计划", "弦计划ProjectString"]),
        ("浙江大学", "产品", ["浙大互联网协会", "浙大学生互联网"]),
        ("上海交通大学", "产品", ["交大创新创业协会", "交大创协", "SJTU双创"]),
        ("复旦大学", "产品", ["复旦互联网联盟", "FDU互联网"]),
        # 技术 - 清华
        ("清华大学", "技术", ["清华算法协会"]),
        ("清华大学", "技术", ["清华超算"]),
        ("清华大学", "技术", ["清华网络安全技术", "清华网络安全协会"]),
        ("清华大学", "技术", ["清华通用人工智能", "清华AGI"]),
        ("清华大学", "技术", ["清华人工智能治理"]),
        ("清华大学", "技术", ["清华大数据研究"]),
        # 技术 - 北大
        ("北京大学", "技术", ["北大人工智能创新", "北大AIIA"]),
        ("北京大学", "技术", ["北大超算"]),
        ("北京大学", "技术", ["北大Linus", "北大Linux俱乐部"]),
        ("北京大学", "技术", ["PKUCC", "北大网络安全战队"]),
        ("北京大学", "技术", ["北大算法协会", "pkusaa"]),
        # 技术 - 浙大
        ("浙江大学", "技术", ["浙大人工智能俱乐部", "浙大AI俱乐部"]),
        ("浙江大学", "技术", ["浙大超算"]),
        ("浙江大学", "技术", ["浙大网络空间安全"]),
        ("浙江大学", "技术", ["Room78", "算法竞赛社"]),
        # 技术 - 上交
        ("上海交通大学", "技术", ["思源极客"]),
        ("上海交通大学", "技术", ["0ops"]),
        ("上海交通大学", "技术", ["Xflops超算", "交大超算"]),
        ("上海交通大学", "技术", ["交龙机器人"]),
        ("上海交通大学", "技术", ["交大人工智能创新", "SJTUAIIA"]),
        # 技术 - 复旦
        ("复旦大学", "技术", ["复旦电子创客", "FudanEGA"]),
        ("复旦大学", "技术", ["复旦网络安全", "复旦信息网络安全"]),
        ("复旦大学", "技术", ["sixstars", "six stars复旦"]),
    ]
    
    all_results = {}
    for university, category, queries in search_list:
        key = f"{university}_{category}_{queries[0]}"
        print(f'\n=== {university} [{category}] - {queries[0]} ===')
        for q in queries:
            results = search_club(crawler, q, limit=3)
            if results:
                all_results[key] = (university, category, results)
                break
            time.sleep(10)
        time.sleep(10)
    
    db.close()
    print('\n\n===== Search complete. Review results above. =====')

if __name__ == '__main__':
    main()
