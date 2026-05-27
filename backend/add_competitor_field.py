"""添加 is_competitor 和 competitor_note 字段到 channels 表"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'data', 'channels.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 检查字段是否已存在
cursor.execute("PRAGMA table_info(channels)")
columns = [col[1] for col in cursor.fetchall()]
print(f"现有字段: {columns}")

if 'is_competitor' not in columns:
    cursor.execute("ALTER TABLE channels ADD COLUMN is_competitor BOOLEAN DEFAULT 0 NOT NULL")
    print("已添加 is_competitor 字段")
else:
    print("is_competitor 字段已存在")

if 'competitor_note' not in columns:
    cursor.execute("ALTER TABLE channels ADD COLUMN competitor_note TEXT DEFAULT ''")
    print("已添加 competitor_note 字段")
else:
    print("competitor_note 字段已存在")

conn.commit()

# 验证
cursor.execute("PRAGMA table_info(channels)")
columns = [col[1] for col in cursor.fetchall()]
print(f"更新后字段: {columns}")

conn.close()
print("迁移完成")
