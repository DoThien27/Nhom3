import pyodbc
import threading

_local = threading.local()

DB_CONFIG = {
    "DRIVER": "{ODBC Driver 17 for SQL Server}",
    "SERVER": "DESKTOP-MKHQEU8",
    "DATABASE": "GymThepDBB",
    "UID": "sa",
    "PWD": "123456",
    "TrustServerCertificate": "yes",
}


def get_connection():
    """Trả về connection (tái sử dụng theo thread)."""
    if not getattr(_local, "conn", None):
        conn_str = ";".join(f"{k}={v}" for k, v in DB_CONFIG.items())
        _local.conn = pyodbc.connect(conn_str, autocommit=False)
    return _local.conn


def close_connection():
    conn = getattr(_local, "conn", None)
    if conn:
        try:
            conn.close()
        except Exception:
            pass
        _local.conn = None


def test_connection() -> bool:
    try:
        conn = get_connection()
        conn.cursor().execute("SELECT 1")
        return True
    except Exception:
        return False
