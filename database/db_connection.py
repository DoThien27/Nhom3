import mysql.connector
import threading
import queue
import os
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "sports_club_db"),
    "connection_timeout": int(os.environ.get("DB_TIMEOUT", "5")),
    "connect_timeout": int(os.environ.get("DB_TIMEOUT", "5")),
}

_POOL_SIZE = 8  # Số connection giữ sẵn


class PyOdbcCompatCursor:
    def __init__(self, raw_conn):
        """raw_conn là mysql.connector raw connection (không phải compat wrapper)."""
        self._raw_conn = raw_conn
        self.cursor = raw_conn.cursor(dictionary=True)

    def execute(self, query, *args):
        query = query.replace("?", "%s")
        if len(args) == 1 and isinstance(args[0], (tuple, list)):
            params = args[0]
        else:
            params = args if args else None

        import mysql.connector
        for attempt in range(2):   # Thử tối đa 2 lần (1 lần reconnect)
            try:
                if params:
                    self.cursor.execute(query, params)
                else:
                    self.cursor.execute(query)
                return  # Thành công
            except mysql.connector.errors.OperationalError as e:
                # Lost connection / server gone away → reconnect và thử lại
                if attempt == 0 and e.errno in (2006, 2013, 2055):
                    print(f"[db] Lost connection, reconnecting... (errno={e.errno})")
                    try:
                        self._raw_conn.reconnect(attempts=3, delay=1)
                        self.cursor = self._raw_conn.cursor(dictionary=True)
                    except Exception as re_err:
                        print(f"[db] Reconnect failed: {re_err}")
                        raise
                else:
                    raise

    def fetchone(self):
        row = self.cursor.fetchone()
        return self._wrap(row) if row else None

    def fetchall(self):
        return [self._wrap(r) for r in self.cursor.fetchall()]

    def _wrap(self, row):
        class Row:
            def __init__(self, d):
                self.__dict__.update(d)
            def __getitem__(self, k):
                return self.__dict__.get(k)
            def __getattr__(self, k):
                return None
        return Row(row)

    def close(self):
        try:
            self.cursor.close()
        except Exception:
            pass


class PyOdbcCompatConnection:
    """Wrapper connection tương thích API cũ."""
    def __init__(self, raw_conn, pool=None):
        self._raw = raw_conn
        self._pool = pool

    def cursor(self, **kwargs):
        """Đảm bảo connection sống trước khi tạo cursor."""
        if not self._raw.is_connected():
            try:
                self._raw.reconnect(attempts=3, delay=1)
            except Exception:
                # Tạo connection mới hoàn toàn
                self._raw = mysql.connector.connect(**DB_CONFIG)
        return PyOdbcCompatCursor(self._raw)
        
    def commit(self):
        self._raw.commit()

    def rollback(self):
        try:
            self._raw.rollback()
        except Exception:
            pass

    def close(self):
        """Trả connection về pool thay vì đóng."""
        if self._pool is not None:
            self._pool._return(self._raw)
            self._pool = None
        else:
            try:
                self._raw.close()
            except Exception:
                pass
        
    def is_connected(self):
        return self._raw.is_connected()


class _ConnectionPool:
    """Pool connection thread-safe — giữ sẵn các connection, phân phát nhanh."""
    def __init__(self, size: int):
        self._size = size
        self._pool: queue.Queue = queue.Queue(maxsize=size)
        self._lock = threading.Lock()

    def _make_raw(self):
        return mysql.connector.connect(**DB_CONFIG)

    def warm_up(self):
        """Tạo sẵn tất cả connection trong pool — gọi 1 lần khi khởi động."""
        for _ in range(self._size):
            try:
                raw = self._make_raw()
                self._pool.put_nowait(raw)
            except Exception:
                pass  # Nếu DB chưa sẵn sàng thì bỏ qua, get() sẽ tự tạo

    def get(self) -> PyOdbcCompatConnection:
        """Lấy connection từ pool (không block, tạo mới nếu pool rỗng)."""
        try:
            raw = self._pool.get_nowait()
            if not raw.is_connected():
                try:
                    raw.reconnect(attempts=3, delay=0)
                except Exception:
                    raw = self._make_raw()
        except queue.Empty:
            raw = self._make_raw()
        return PyOdbcCompatConnection(raw, pool=self)

    def _return(self, raw):
        """Trả connection về pool sau khi dùng xong."""
        try:
            raw.rollback()
        except Exception:
            pass
        try:
            self._pool.put_nowait(raw)
        except queue.Full:
            try:
                raw.close()
            except Exception:
                pass


# Singleton pool
_pool = _ConnectionPool(_POOL_SIZE)


def warm_up():
    """Gọi 1 lần khi app khởi động để tạo sẵn các connection."""
    t = threading.Thread(target=_pool.warm_up, daemon=True)
    t.start()


def get_connection() -> PyOdbcCompatConnection:
    """Lấy connection từ pool (nhanh vì đã warm-up sẵn)."""
    return _pool.get()


def close_connection():
    """Không cần gọi thủ công — connection tự trả pool sau khi dùng."""
    pass


def test_connection() -> bool:
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.fetchall()
        cur.close()
        conn.close()  # trả về pool
        return True
    except Exception:
        return False

@contextmanager
def get_db_context():
    """
    Context manager to safely yield a (connection, cursor) tuple.
    Automatically closes the cursor and returns the connection to the pool.
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        yield conn, cur
    finally:
        try:
            cur.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass
