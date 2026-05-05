from typing import List, Optional
from database.db_connection import get_db_context
from utils.logger import logger
from models.models import GoiTap


def lay_tat_ca() -> List[GoiTap]:
    try:
        with get_db_context() as (conn, cur):
            cur.execute("SELECT * FROM Plans ORDER BY price")
            plans = []
            for row in cur.fetchall():
                plans.append(GoiTap(
                    id=str(row.id),
                    ten=row.name or "",
                    loai=row.type or "MEMBERSHIP",
                    gia=float(row.price) if row.price else 0.0,
                    mo_ta=row.description or "",
                    thoi_han_thang=row.durationMonths,
                    so_buoi=row.sessions,
                ))
            return plans
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise


def lay_theo_id(id_goi: str) -> Optional[GoiTap]:
    try:
        with get_db_context() as (conn, cur):
            cur.execute("SELECT * FROM Plans WHERE id=%s", (id_goi,))
            row = cur.fetchone()
            if not row:
                return None
            return GoiTap(
                id=str(row.id),
                ten=row.name or "",
                loai=row.type or "MEMBERSHIP",
                gia=float(row.price) if row.price else 0.0,
                mo_ta=row.description or "",
                thoi_han_thang=row.durationMonths,
                so_buoi=row.sessions,
            )
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise


def them(goi_tap: GoiTap) -> GoiTap:
    try:
        with get_db_context() as (conn, cur):
            cur.execute(
                "INSERT INTO Plans (id, name, type, price, description, durationMonths, sessions) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (goi_tap.id, goi_tap.ten, goi_tap.loai, goi_tap.gia,
                 goi_tap.mo_ta, goi_tap.thoi_han_thang, goi_tap.so_buoi)
            )
            conn.commit()
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise
    return goi_tap


def cap_nhat(goi_tap: GoiTap) -> GoiTap:
    try:
        with get_db_context() as (conn, cur):
            cur.execute(
                "UPDATE Plans SET name=%s, type=%s, price=%s, description=%s, "
                "durationMonths=%s, sessions=%s WHERE id=%s",
                (goi_tap.ten, goi_tap.loai, goi_tap.gia, goi_tap.mo_ta,
                 goi_tap.thoi_han_thang, goi_tap.so_buoi, goi_tap.id)
            )
            conn.commit()
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise
    return goi_tap


def xoa(id_goi_tap: str) -> None:
    try:
        with get_db_context() as (conn, cur):
            cur.execute("DELETE FROM Plans WHERE id=%s", (id_goi_tap,))
            conn.commit()
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise
