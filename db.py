import os, sqlite3
from pathlib import Path

DB_PATH = Path(os.getenv("DB_PATH","/mnt/data/milla_bot.sqlite3"))

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS kv (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            source TEXT NOT NULL,
            kind TEXT NOT NULL,
            client TEXT,
            title TEXT,
            payload TEXT
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS tracked_clients (
            name TEXT PRIMARY KEY
        )
        """)
        conn.commit()

def kv_get(key, default=None):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT value FROM kv WHERE key=?", (key,))
        row = cur.fetchone()
        return row[0] if row else default

def kv_set(key, value):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO kv(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, str(value)))
        conn.commit()

def add_event(source, kind, client=None, title=None, payload=None, ts=None):
    import datetime
    ts = ts or datetime.datetime.utcnow().isoformat()
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO events(ts,source,kind,client,title,payload) VALUES(?,?,?,?,?,?)",
                    (ts,source,kind,client,title, payload if payload is None else str(payload)))
        conn.commit()

def list_events(limit=50):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT ts,source,kind,client,title,payload FROM events ORDER BY id DESC LIMIT ?", (limit,))
        return cur.fetchall()

def add_tracked_client(name):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("INSERT OR IGNORE INTO tracked_clients(name) VALUES(?)",(name,))
        conn.commit()

def remove_tracked_client(name):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM tracked_clients WHERE name=?",(name,))
        conn.commit()

def get_tracked_clients():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM tracked_clients ORDER BY name")
        return [r[0] for r in cur.fetchall()]
