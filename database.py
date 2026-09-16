import sqlite3
from datetime import datetime, timezone
from pathlib import Path

class Database:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript('''
        CREATE TABLE IF NOT EXISTS tweets (tweet_id TEXT PRIMARY KEY, author_id TEXT, author TEXT, text TEXT, url TEXT, created_at TEXT, likes INTEGER DEFAULT 0, replies INTEGER DEFAULT 0, keyword TEXT, seen_at TEXT);
        CREATE TABLE IF NOT EXISTS replies (tweet_id TEXT PRIMARY KEY, reply TEXT, status TEXT, reply_url TEXT, style TEXT, created_at TEXT, likes INTEGER DEFAULT 0, replies_count INTEGER DEFAULT 0, reposts INTEGER DEFAULT 0, impressions INTEGER);
        CREATE TABLE IF NOT EXISTS authors (author_id TEXT PRIMARY KEY, last_reply_at TEXT, replies_today INTEGER DEFAULT 0);
        CREATE TABLE IF NOT EXISTS errors (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT, context TEXT, error TEXT);
        '''); self.conn.commit()
    def seen(self, tweet_id): return self.conn.execute('SELECT 1 FROM tweets WHERE tweet_id=?', (str(tweet_id),)).fetchone() is not None
    def has_reply_record(self, tweet_id): return self.conn.execute('SELECT 1 FROM replies WHERE tweet_id=?', (str(tweet_id),)).fetchone() is not None
    def author_count_today(self, author_id):
        row=self.conn.execute("SELECT COUNT(*) n FROM replies r JOIN tweets t ON t.tweet_id=r.tweet_id WHERE t.author_id=? AND r.status IN ('POSTED','DRY_RUN') AND date(r.created_at)=date('now')", (str(author_id),)).fetchone(); return row['n']
    def posted_count_today(self):
        row=self.conn.execute("SELECT COUNT(*) n FROM replies WHERE status='POSTED' AND date(created_at)=date('now')").fetchone(); return row['n']
    def record_tweet(self, t, keyword):
        self.conn.execute('INSERT OR IGNORE INTO tweets VALUES (?,?,?,?,?,?,?,?,?,?)', (str(t.id),str(t.author_id),t.author,t.text,t.url,t.created_at,t.likes,t.replies,keyword,datetime.now(timezone.utc).isoformat())); self.conn.commit()
    def record_reply(self, tweet_id, reply, status, url='', style=''):
        self.conn.execute('INSERT OR REPLACE INTO replies(tweet_id,reply,status,reply_url,style,created_at) VALUES(?,?,?,?,?,?)',(str(tweet_id),reply,status,url,style,datetime.now(timezone.utc).isoformat())); self.conn.commit()
    def record_error(self, context, error): self.conn.execute('INSERT INTO errors(created_at,context,error) VALUES(?,?,?)',(datetime.now(timezone.utc).isoformat(),context,str(error))); self.conn.commit()
    def recent_replies(self, limit=100): return self.conn.execute('SELECT reply FROM replies ORDER BY created_at DESC LIMIT ?', (limit,)).fetchall()
