import sys, os, time
sys.path.insert(0, os.path.dirname('.'))
from app.database import get_db
from app.models import Channel
from app.services.wechat_crawler import WeChatCrawler
from app.config import settings

crawler = WeChatCrawler(token=settings.wechat_token, cookie=settings.wechat_cookie)

# Search for the account
print('Searching: 竞在燕园')
results = crawler.search_accounts('竞在燕园', limit=5)
if results:
    for r in results:
        nickname = r.get('nickname', '')
        fakeid = r.get('fakeid', '')
        print(f'  {nickname} (fakeid={fakeid})')
    
    # Add the first match
    r = results[0]
    db = next(get_db())
    fakeid = r.get('fakeid', '')
    
    # Check duplicate
    dup = db.query(Channel).filter(Channel.fakeid == fakeid).first()
    if dup:
        print(f'Already exists: {dup.nickname}')
    else:
        channel = Channel(
            fakeid=fakeid,
            nickname=r.get('nickname', ''),
            avatar_url=r.get('round_head_url', ''),
            university_name='北京大学',
            category='游戏',
            is_active=True
        )
        db.add(channel)
        db.commit()
        db.refresh(channel)
        print(f'Added: {channel.nickname} (id={channel.id})')
    db.close()
else:
    print('No results found for 竞在燕园')
