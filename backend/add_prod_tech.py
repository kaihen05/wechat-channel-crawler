"""
Add product and tech clubs from PPT to database.
Searches WeChat for each club, adds matches with human verification.
"""
import sys, os, time
sys.path.insert(0, os.path.dirname('.'))
from app.database import get_db
from app.models import Channel, Article
from app.services.wechat_crawler import WeChatCrawler
from app.config import settings

# Clubs to add: (university, category, search_query, ppt_name)
PRODUCT_CLUBS = [
    ("清华大学", "产品", "清华互联网产品研究协会", "清华大学互联网产品研究协会"),
    ("清华大学", "产品", "AttraX", "AttraX"),
    ("北京大学", "产品", "清华互联网产品研究协会", "清华大学互联网产品研究协会"),  # PPT lists this for PKU too
    ("浙江大学", "产品", "弦计划", "弦计划"),
    ("浙江大学", "产品", "浙大互联网协会", "浙江大学学生互联网协会"),
    ("上海交通大学", "产品", "交大创新创业协会", "交大创新创业协会"),
    ("复旦大学", "产品", "FDU互联网协会", "FDU互联网协会"),
]

TECH_CLUBS = [
    # 清华
    ("清华大学", "技术", "清华算法协会", "清华大学算法协会"),
    ("清华大学", "技术", "清华超算队", "清华超算队"),
    ("清华大学", "技术", "清华网络安全技术协会", "清华大学网络学生安全技术协会"),
    ("清华大学", "技术", "清华通用人工智能协会", "清华大学通用人工智能协会"),
    ("清华大学", "技术", "清华人工智能治理协会", "清华大学学生人工智能治理协会"),
    ("清华大学", "技术", "清华大数据研究协会", "清华大学大数据研究协会"),
    # 北大
    ("北京大学", "技术", "北大人工智能创新协会", "北大学生人工智能创新协会"),
    ("北京大学", "技术", "北大超算队", "北大超算队"),
    ("北京大学", "技术", "北大Linus俱乐部", "北京大学学生Linus俱乐部"),
    ("北京大学", "技术", "PKUCC北大网络安全", "PKUCC北大网络安全战队"),
    ("北京大学", "技术", "北大算法协会", "北京大学算法协会"),
    # 浙大
    ("浙江大学", "技术", "浙大人工智能俱乐部", "浙大人工智能俱乐部"),
    ("浙江大学", "技术", "浙大超算队", "浙大超算队"),
    ("浙江大学", "技术", "浙大网络空间安全协会", "浙江大学学生网络空间安全协会"),
    ("浙江大学", "技术", "Room78算法竞赛", "Room78算法竞赛社"),
    # 上交
    ("上海交通大学", "技术", "思源极客", "思源极客"),
    ("上海交通大学", "技术", "0ops网络安全", "0ops网络安全竞赛团队"),
    ("上海交通大学", "技术", "交大Xflops超算", "上海交通大学Xflops超算队"),
    ("上海交通大学", "技术", "交大交龙机器人", "上海交大交龙机器人俱乐部"),
    ("上海交通大学", "技术", "交大人工智能创新协会", "上海交通大学人工智能创新协会"),
    # 复旦
    ("复旦大学", "技术", "复旦电子创客", "复旦大学电子创客社团"),
    ("复旦大学", "技术", "复旦信息网络安全协会", "复旦大学信息网络安全协会"),
    ("复旦大学", "技术", "sixstars", "sixstars"),
]

def search_and_add(crawler, db, university, category, search_query, ppt_name, dry_run=False):
    """Search for a club on WeChat and add to database."""
    print(f'\n--- Searching: {ppt_name} ({university}) [{category}] ---')
    print(f'    Query: {search_query}')
    
    results = crawler.search_accounts(search_query, limit=5)
    if not results:
        print('    ❌ No results found')
        return None
    
    for r in results:
        nickname = r.get('nickname', '')
        fakeid = r.get('fakeid', '')
        sig = r.get('signature', '')[:50] if r.get('signature') else ''
        print(f'    Found: {nickname} (fakeid={fakeid}) sig={sig}')
    
    # Try to find best match
    best = None
    best_score = 0
    search_lower = search_query.lower()
    ppt_lower = ppt_name.lower()
    
    for r in results:
        nickname = r.get('nickname', '')
        nickname_lower = nickname.lower()
        
        # Calculate match score
        score = 0
        # Check if key parts of search query appear in nickname
        for word in search_lower.replace('大学', '').replace('学生', '').replace('协会', '').replace('俱乐部', ''):
            if word in nickname_lower:
                score += 1
        
        # Check if key parts of nickname appear in search query
        for word in nickname_lower.replace('大学', '').replace('学生', '').replace('协会', '').replace('俱乐部', ''):
            if word in search_lower:
                score += 1
        
        # Bonus for exact keyword matches
        key_terms = [t for t in [ppt_lower, search_lower] if len(t) > 2]
        for term in key_terms:
            if term in nickname_lower or nickname_lower in term:
                score += 10
        
        if score > best_score:
            best_score = score
            best = r
    
    if not best:
        print('    ❌ No good match found')
        return None
    
    nickname = best.get('nickname', '')
    fakeid = best.get('fakeid', '')
    
    # Check duplicate
    dup = db.query(Channel).filter(Channel.fakeid == fakeid).first()
    if dup:
        print(f'    ⚠️ Already exists: {dup.nickname} (id={dup.id}, cat={dup.category})')
        return dup
    
    if best_score < 5:
        print(f'    ⚠️ Low confidence match (score={best_score}): {nickname}')
        print(f'    Skipping - manual verification needed')
        return None
    
    if dry_run:
        print(f'    [DRY RUN] Would add: {nickname} -> {university} [{category}]')
        return None
    
    channel = Channel(
        fakeid=fakeid,
        nickname=nickname,
        avatar_url=best.get('round_head_url', ''),
        university_name=university,
        category=category,
        is_active=True
    )
    db.add(channel)
    db.commit()
    db.refresh(channel)
    print(f'    ✅ Added: {nickname} (id={channel.id}) -> {university} [{category}]')
    return channel


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--category', choices=['产品', '技术', 'all'], default='all')
    args = parser.parse_args()
    
    crawler = WeChatCrawler(token=settings.wechat_token, cookie=settings.wechat_cookie)
    db = next(get_db())
    
    # Delete test channel
    test_ch = db.query(Channel).filter(Channel.nickname == '测试技术公众号').first()
    if test_ch:
        db.query(Article).filter(Article.channel_id == test_ch.id).delete()
        db.delete(test_ch)
        db.commit()
        print(f'Deleted test channel: {test_ch.nickname}')
    
    clubs = []
    if args.category in ['产品', 'all']:
        clubs.extend(PRODUCT_CLUBS)
    if args.category in ['技术', 'all']:
        clubs.extend(TECH_CLUBS)
    
    added = 0
    skipped = 0
    
    for university, category, search_query, ppt_name in clubs:
        result = search_and_add(crawler, db, university, category, search_query, ppt_name, dry_run=args.dry_run)
        if result:
            added += 1
        else:
            skipped += 1
        time.sleep(12)  # Rate limit
    
    print(f'\n===== Summary =====')
    print(f'Added: {added}')
    print(f'Skipped: {skipped}')
    
    # Show all channels by category
    for cat in ['产品', '技术']:
        channels = db.query(Channel).filter(Channel.category == cat).all()
        print(f'\n=== {cat} channels ({len(channels)}) ===')
        for c in channels:
            print(f'  {c.university_name} | {c.nickname}')
    
    db.close()


if __name__ == '__main__':
    main()
