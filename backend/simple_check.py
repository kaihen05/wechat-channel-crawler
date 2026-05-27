import sqlite3
import sys

db_path = 'C:/Users/kaiboy/Desktop/wechat-channel-crawler/backend/data/channels.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 检查表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Tables:", cursor.fetchall())

# 检查 channels 表结构
cursor.execute("PRAGMA table_info(channels)")
columns = cursor.fetchall()
print("\nChannels 表结构:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

# 检查前5条 channel 数据
cursor.execute("SELECT id, nickname, total_read_num FROM channels LIMIT 5")
channels = cursor.fetchall()
print("\n前5个公众号:")
for ch in channels:
    print(f"  ID: {ch[0]}, 名称: {ch[1]}, 累计阅读: {ch[2]}")

# 检查文章数据
cursor.execute("SELECT COUNT(*) FROM articles")
article_count = cursor.fetchone()[0]
print(f"\n文章总数: {article_count}")

# 检查前几篇文章
cursor.execute("SELECT id, title, read_num FROM articles LIMIT 5")
articles = cursor.fetchall()
print("\n前5篇文章:")
for art in articles:
    print(f"  ID: {art[0]}, 标题: {art[1][:30] if art[1] else 'N/A'}, 阅读: {art[2]}")

# 计算每个公众号的实际阅读量
print("\n公众号实际阅读量统计:")
for ch in channels:
    cursor.execute("SELECT SUM(read_num) FROM articles WHERE channel_id = ?", (ch[0],))
    total = cursor.fetchone()[0] or 0
    print(f"  {ch[1]}: 数据库={ch[2]}, 实际计算={total}")

conn.close()
