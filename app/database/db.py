"""
app/database/db.py
──────────────────
Connection pool & context manager duy nhat cho toan bo app.
"""
import mysql.connector
import threading
import queue
import os
import sys
import logging
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

# ─── Logger ──────────────────────────────────────────────────────────────────
def _setup_logger():
    log = logging.getLogger("sports_club")
    if not log.handlers:
        log.setLevel(logging.INFO)
        fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        h = logging.StreamHandler(sys.stdout)
        h.setFormatter(fmt)
        log.addHandler(h)
    return log

logger = _setup_logger()

# ─── DB Config ───────────────────────────────────────────────────────────────
DB_CONFIG = {
    "host":               os.environ.get("DB_HOST", "localhost"),
    "user":               os.environ.get("DB_USER", "root"),
    "password":           os.environ.get("DB_PASSWORD", ""),
    "database":           os.environ.get("DB_NAME", "sports_club_db"),
    "connection_timeout": int(os.environ.get("DB_TIMEOUT", "5")),
}

# ─── Compat Wrappers ─────────────────────────────────────────────────────────
class PyOdbcCompatCursor:
    def __init__(self, raw_conn):
        self._raw_conn = raw_conn
        self.cursor = raw_conn.cursor(dictionary=True)
        self.rowcount = 0

    def execute(self, query, params=None):
        query = query.replace("?", "%s")
        try:
            self.cursor.execute(query, params)
            self.rowcount = self.cursor.rowcount
        except mysql.connector.errors.OperationalError as e:
            if e.errno in (2006, 2013, 2055):
                self._raw_conn.reconnect(attempts=3, delay=1)
                self.cursor = self._raw_conn.cursor(dictionary=True)
                self.cursor.execute(query, params)
                self.rowcount = self.cursor.rowcount
            else:
                raise

    def fetchone(self):
        row = self.cursor.fetchone()
        return self._wrap(row) if row else None

    def fetchall(self):
        return [self._wrap(r) for r in self.cursor.fetchall()]

    def _wrap(self, row):
        class Row:
            def __init__(self, d): self.__dict__.update(d)
            def __getitem__(self, k): return self.__dict__.get(k)
            def __iter__(self): return iter(self.__dict__)
            def keys(self): return self.__dict__.keys()
            def get(self, k, default=None): return self.__dict__.get(k, default)
            def items(self): return self.__dict__.items()
            def __contains__(self, k): return k in self.__dict__
        return Row(row)

    def close(self):
        try: self.cursor.close()
        except: pass


class PyOdbcCompatConnection:
    def __init__(self, raw_conn, pool=None):
        self._raw = raw_conn
        self._pool = pool

    def cursor(self, **_):
        if not self._raw.is_connected():
            self._raw.reconnect(attempts=3, delay=1)
        return PyOdbcCompatCursor(self._raw)

    def commit(self): self._raw.commit()
    def rollback(self):
        try: self._raw.rollback()
        except: pass

    def close(self):
        if self._pool:
            self._pool._return(self._raw)
            self._pool = None
        else:
            try: self._raw.close()
            except: pass


# ─── Connection Pool ─────────────────────────────────────────────────────────
class _ConnectionPool:
    def __init__(self, size: int = 8):
        self._size = size
        self._pool = queue.Queue(maxsize=size)

    def _make_raw(self):
        return mysql.connector.connect(**DB_CONFIG)

    def warm_up(self):
        for _ in range(self._size):
            try: self._pool.put_nowait(self._make_raw())
            except: pass

    def get(self):
        try:
            raw = self._pool.get_nowait()
            if not raw.is_connected():
                raw.reconnect(attempts=3, delay=0)
        except queue.Empty:
            raw = self._make_raw()
        return PyOdbcCompatConnection(raw, pool=self)

    def _return(self, raw):
        try: raw.rollback()
        except: pass
        try: self._pool.put_nowait(raw)
        except queue.Full:
            try: raw.close()
            except: pass


_pool = _ConnectionPool(8)


def warm_up():
    """Khoi dong pool ngam trong background thread."""
    threading.Thread(target=_pool.warm_up, daemon=True).start()


def get_connection():
    return _pool.get()


@contextmanager
def get_db_context():
    """Context manager: yield (conn, cur), tu dong dong khi xong."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        yield conn, cur
    finally:
        try: cur.close()
        except: pass
        try: conn.close()
        except: pass
