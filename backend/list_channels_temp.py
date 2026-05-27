import sqlite3
conn = sqlite3.connect('data/channels.db')
cursor = conn.cursor()
cursor.execute('SELECT id, nickname, category FROM channels ORDER BY category, nickname')
for r in cursor.fetchall():
    print(f"ID={r[0]:3d} | {r[2]:4s} | {r[1]}")
conn.close()
