#!/bin/bash
cd /workspace

# Ensure data directory exists
mkdir -p data

# Import seed data if database is empty
python3 -c "
import sqlite3, os
db_path = 'data/channels.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Check if channels table exists and has data
try:
    c.execute('SELECT COUNT(*) FROM channels')
    count = c.fetchone()[0]
except:
    count = 0

if count == 0:
    print('Database empty, importing seed data...')
    seed_file = 'data/seed_data.sql'
    if os.path.exists(seed_file):
        with open(seed_file, 'r', encoding='utf-8') as f:
            sql = f.read()
        # Adapt for new columns: is_competitor, competitor_keywords, competitor_note
        sql = sql.replace(
            'university_name, category, is_active, created_at, updated_at, last_sync_at, total_read_num)',
            'university_name, category, is_active, is_competitor, competitor_keywords, competitor_note, created_at, updated_at, last_sync_at, total_read_num)'
        )
        for cat in ['游戏', '综合', '人力', '产品', '技术']:
            sql = sql.replace(
                f\"'{cat}', 1, '2026-\",
                f\"'{cat}', 1, 0, '', '', '2026-\"
            )
        c.executescript(sql)
        conn.commit()
        c.execute('SELECT COUNT(*) FROM channels')
        ch_count = c.fetchone()[0]
        c.execute('SELECT COUNT(*) FROM articles')
        art_count = c.fetchone()[0]
        print(f'Imported {ch_count} channels, {art_count} articles')
    else:
        print(f'WARNING: Seed data file not found: {seed_file}')
else:
    print(f'Database already has {count} channels')
conn.close()
"

# Start the application
exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
