from typing import List, Optional
from dataclasses import dataclass
from database.db_connection import get_db_context
from utils.logger import logger


@dataclass
class MonTheThao:
    id: str
    ten: str
    mo_ta: str = ""
    trang_thai: str = "ACTIVE"


def lay_tat_ca() -> List[MonTheThao]:
    try:
        with get_db_context() as (conn, cur):
            cur.execute("SELECT sport_id, sport_name, description, status FROM Sports ORDER BY sport_name")
            return [
                MonTheThao(
                    id=str(row.sport_id),
                    ten=row.sport_name or "",
                    mo_ta=row.description or "",
                    trang_thai=row.status or "ACTIVE",
                )
                for row in cur.fetchall()
            ]
    except Exception as e:
        logger.error(f"[sport_service] lay_tat_ca ERROR: {e}")
        return []


def them(mon: MonTheThao) -> MonTheThao:
    try:
        with get_db_context() as (conn, cur):
            cur.execute(
                "INSERT INTO Sports (sport_id, sport_name, description, status) VALUES (%s,%s,%s,%s)",
                (mon.id, mon.ten, mon.mo_ta, mon.trang_thai)
            )
            conn.commit()
        return mon
    except Exception as e:
        logger.error(f"[sport_service] them ERROR: {e}")
        raise


def cap_nhat(mon: MonTheThao) -> MonTheThao:
    try:
        with get_db_context() as (conn, cur):
            cur.execute(
                "UPDATE Sports SET sport_name=%s, description=%s, status=%s WHERE sport_id=%s",
                (mon.ten, mon.mo_ta, mon.trang_thai, mon.id)
            )
            conn.commit()
        return mon
    except Exception as e:
        logger.error(f"[sport_service] cap_nhat ERROR: {e}")
        raise


def xoa(id_mon: str) -> None:
    try:
        with get_db_context() as (conn, cur):
            cur.execute("DELETE FROM Sports WHERE sport_id=%s", (id_mon,))
            conn.commit()
    except Exception as e:
        logger.error(f"[sport_service] xoa ERROR: {e}")
        raise
