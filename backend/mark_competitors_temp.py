import sqlite3
conn = sqlite3.connect('data/channels.db')
cursor = conn.cursor()
cursor.execute("UPDATE channels SET is_competitor = 1, competitor_note = category WHERE is_competitor = 0")
affected = cursor.rowcount
conn.commit()
print(f"已标记 {affected} 个公众号为友商")

cursor.execute("SELECT nickname, competitor_note FROM channels WHERE is_competitor = 1")
for r in cursor.fetchall():
    print(f"  ✓ {r[0]}（{r[1]}）")
conn.close()
