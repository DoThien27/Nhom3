from typing import List
from dataclasses import dataclass
from database.db_connection import get_db_context
from utils.logger import logger


@dataclass
class SanBai:
    id: str
    ten: str
    loai: str = ""
    vi_tri: str = ""
    suc_chua: int = 0
    rental_price: float = 0.0
    trang_thai: str = "ACTIVE"


def lay_tat_ca() -> List[SanBai]:
    try:
        with get_db_context() as (conn, cur):
            cur.execute(
                "SELECT facility_id, facility_name, facility_type, location, "
                "capacity, rental_price, status FROM Facilities ORDER BY facility_name"
            )
            return [
                SanBai(
                    id=str(row.facility_id),
                    ten=row.facility_name or "",
                    loai=row.facility_type or "",
                    vi_tri=row.location or "",
                    suc_chua=int(row.capacity) if row.capacity else 0,
                    rental_price=float(row.rental_price) if row.rental_price else 0.0,
                    trang_thai=row.status or "ACTIVE",
                )
                for row in cur.fetchall()
            ]
    except Exception as e:
        logger.error(f"[facility_service] lay_tat_ca ERROR: {e}")
        return []


def them(san: SanBai) -> SanBai:
    try:
        with get_db_context() as (conn, cur):
            cur.execute(
                "INSERT INTO Facilities (facility_id, facility_name, facility_type, location, capacity, rental_price, status) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (san.id, san.ten, san.loai, san.vi_tri, san.suc_chua, san.rental_price, san.trang_thai)
            )
            conn.commit()
        return san
    except Exception as e:
        logger.error(f"[facility_service] them ERROR: {e}")
        raise


def cap_nhat(san: SanBai) -> SanBai:
    try:
        with get_db_context() as (conn, cur):
            cur.execute(
                "UPDATE Facilities SET facility_name=%s, facility_type=%s, location=%s, "
                "capacity=%s, rental_price=%s, status=%s WHERE facility_id=%s",
                (san.ten, san.loai, san.vi_tri, san.suc_chua, san.rental_price, san.trang_thai, san.id)
            )
            conn.commit()
        return san
    except Exception as e:
        logger.error(f"[facility_service] cap_nhat ERROR: {e}")
        raise


def xoa(id_san: str) -> None:
    try:
        with get_db_context() as (conn, cur):
            cur.execute("DELETE FROM Facilities WHERE facility_id=%s", (id_san,))
            conn.commit()
    except Exception as e:
        logger.error(f"[facility_service] xoa ERROR: {e}")
        raise
