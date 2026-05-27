import sys
sys.path.insert(0, '/data/workspace')
from app.database import init_db
init_db()
print('Database initialized at /data/workspace/data/channels.db')
