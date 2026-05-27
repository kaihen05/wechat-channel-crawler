#!/usr/bin/env python
"""检查数据库中的文章 msgid"""
from app.database import SessionLocal
from app.models import Article

db = SessionLocal()
try:
    articles = db.query(Article).limit(10).all()
    print(f"数据库中共有 {db.query(Article).count()} 篇文章")
    print(f"\n前10篇文章的msgid:")
    print("-" * 80)
    for a in articles:
        print(f"ID: {a.id}")
        print(f"  Title: {a.title[:50]}")
        print(f"  msgid: {a.msgid or '空'}")
        print(f"  Link: {a.link[:80] if a.link else '空'}")
        print("-" * 80)
finally:
    db.close()
