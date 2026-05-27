"""
Add verified product and tech clubs to database.
Only adds clubs with confirmed WeChat accounts.
"""
import sys, os
sys.path.insert(0, os.path.dirname('.'))
from app.database import get_db
from app.models import Channel, Article
from app.services.wechat_crawler import WeChatCrawler
from app.config import settings
from sqlalchemy import func

# Verified matches: (university, category, nickname, fakeid)
VERIFIED_CLUBS = [
    # === 产品 ===
    ("清华大学", "产品", "AttraX", "MzcwNjEzNDI3Mg=="),
    ("浙江大学", "产品", "弦计划ProjectString", "Mzg2MTY3Njg5NA=="),
    ("上海交通大学", "产品", "交大创协", "MzU1NjU2MTQwMA=="),
    ("复旦大学", "产品", "复旦互联网联盟", "MzU3Mjc5NTgwNg=="),
    
    # === 技术 - 清华 ===
    ("清华大学", "技术", "清华大学学生网络安全技术协会", "MzA5MjUwOTY4Ng=="),
    ("清华大学", "技术", "THUAGI", "Mzk0ODYyNTI3Nw=="),
    ("清华大学", "技术", "数据派THU", "MzI1MjQ2OTQ3Ng=="),
    
    # === 技术 - 北大 ===
    ("北京大学", "技术", "pkuCC", "MjM5NzY5OTQxMQ=="),
    ("北京大学", "技术", "北京大学学生 Linux 俱乐部", "Mzk0OTY1ODc0Nw=="),
    ("北京大学", "技术", "PKUSAA", "Mzg4NjExNDUzMg=="),
    
    # === 技术 - 浙大 ===
    ("浙江大学", "技术", "浙大网安", "Mzg5NDczNDc4NA=="),
    ("浙江大学", "技术", "Room78算法竞赛社", "MzkzNDE1NjUzMA=="),
    ("浙江大学", "技术", "ZJUSCT", "Mzg4MDQ3NjIyMQ=="),
    
    # === 技术 - 上交 ===
    ("上海交通大学", "技术", "0ops", "MzcwNjEyMzMxNA=="),
    ("上海交通大学", "技术", "上海交大交龙机器人俱乐部", "MzIzMDgyOTA1MQ=="),
    
    # === 技术 - 复旦 ===
    ("复旦大学", "技术", "FudanEGA电子创客社团", "MzU2NjkyMTkwMA=="),
]

def main():
    crawler = WeChatCrawler(token=settings.wechat_token, cookie=settings.wechat_cookie)
    db = next(get_db())
    
    added = 0
    skipped = 0
    
    for university, category, nickname, fakeid in VERIFIED_CLUBS:
        # Check duplicate
        dup = db.query(Channel).filter(Channel.fakeid == fakeid).first()
        if dup:
            print(f'⚠️ Duplicate: {dup.nickname} (id={dup.id}, cat={dup.category})')
            skipped += 1
            continue
        
        # Try to get avatar from search
        avatar_url = ''
        try:
            results = crawler.search_accounts(nickname, limit=1)
            if results:
                for r in results:
                    if r.get('fakeid') == fakeid:
                        avatar_url = r.get('round_head_url', '')
                        break
        except:
            pass
        
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
        print(f'✅ Added: {nickname} -> {university} [{category}] (id={channel.id})')
        added += 1
    
    print(f'\n===== Added: {added}, Skipped: {skipped} =====')
    
    # Show all by category
    for cat in ['产品', '技术']:
        channels = db.query(Channel).filter(Channel.category == cat).all()
        print(f'\n=== {cat} ({len(channels)}) ===')
        for c in channels:
            art_count = db.query(Article).filter(Article.channel_id == c.id).count()
            print(f'  {c.university_name} | {c.nickname} | {art_count} articles')
    
    db.close()

if __name__ == '__main__':
    main()
