import sqlite3
conn = sqlite3.connect('data/channels.db')
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM channels')
print('channels count:', cursor.fetchone()[0])

cursor.execute('SELECT COUNT(*) FROM articles')
print('articles count:', cursor.fetchone()[0])

cursor.execute('SELECT DISTINCT category FROM channels')
print('categories:', [r[0] for r in cursor.fetchall()])

cursor.execute('SELECT nickname, category FROM channels LIMIT 20')
print('=== sample channels ===')
for r in cursor.fetchall():
    print(r)

cursor.execute('SELECT c.nickname, a.title, a.create_time FROM articles a JOIN channels c ON a.channel_id = c.id ORDER BY a.create_time DESC LIMIT 10')
print('=== recent articles ===')
for r in cursor.fetchall():
    print(r)

conn.close()
