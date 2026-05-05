from typing import List
from database.db_connection import get_db_context
from utils.logger import logger
from models.models import BuoiHoc


def lay_tat_ca() -> List[BuoiHoc]:
    try:
        with get_db_context() as (conn, cur):
            cur.execute("SELECT * FROM Classes")
            classes_rows = cur.fetchall()
            cur.execute("SELECT * FROM ClassEnrollments")
            enrollments = cur.fetchall()
            
            # Tối ưu: Dùng dictionary mapping thay vì vòng lặp lồng nhau O(n*m)
            enroll_map = {}
            for e in enrollments:
                cid = str(e.classId)
                if cid not in enroll_map:
                    enroll_map[cid] = []
                enroll_map[cid].append(str(e.memberId))

            classes = []
            for row in classes_rows:
                enrolled = enroll_map.get(str(row.id), [])
                classes.append(BuoiHoc(
                    id=str(row.id),
                    ten=row.name or "",
                    id_hlv=str(row.trainerId) if row.trainerId else "",
                    gio=row.time or "",
                    thu_trong_tuan=row.dayOfWeek or "",
                    suc_chua=int(row.capacity) if row.capacity else 20,
                    gia=float(row.price) if hasattr(row, 'price') and row.price else 0.0,
                    danh_sach_id_hoi_vien=enrolled
                ))
            return classes
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise


def them(buoi_hoc: BuoiHoc) -> BuoiHoc:
    try:
        with get_db_context() as (conn, cur):
            cur.execute(
                "INSERT INTO Classes (id, name, trainerId, time, dayOfWeek, capacity, price) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (buoi_hoc.id, buoi_hoc.ten, buoi_hoc.id_hlv,
                 buoi_hoc.gio, buoi_hoc.thu_trong_tuan, buoi_hoc.suc_chua, buoi_hoc.gia)
            )
            conn.commit()
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise
    return buoi_hoc


def cap_nhat(buoi_hoc: BuoiHoc) -> BuoiHoc:
    try:
        with get_db_context() as (conn, cur):
            cur.execute(
                "UPDATE Classes SET name=%s, trainerId=%s, time=%s, dayOfWeek=%s, capacity=%s, price=%s WHERE id=%s",
                (buoi_hoc.ten, buoi_hoc.id_hlv, buoi_hoc.gio,
                 buoi_hoc.thu_trong_tuan, buoi_hoc.suc_chua, buoi_hoc.gia, buoi_hoc.id)
            )
            conn.commit()
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise
    return buoi_hoc


def them_hoc_vien(id_lop: str, id_hoi_vien: str) -> bool:
    """Đăng ký hội viên vào lớp học"""
    try:
        with get_db_context() as (conn, cur):
            cur.execute(
                "SELECT 1 FROM ClassEnrollments WHERE classId=%s AND memberId=%s",
                (id_lop, id_hoi_vien)
            )
            if cur.fetchone():
                return False
            cur.execute(
                "INSERT INTO ClassEnrollments (classId, memberId) VALUES (%s,%s)",
                (id_lop, id_hoi_vien)
            )
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise


def xoa_hoc_vien(id_lop: str, id_hoi_vien: str) -> None:
    """Xóa hội viên khỏi lớp học"""
    try:
        with get_db_context() as (conn, cur):
            cur.execute(
                "DELETE FROM ClassEnrollments WHERE classId=%s AND memberId=%s",
                (id_lop, id_hoi_vien)
            )
            conn.commit()
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise


def xoa(id_buoi_hoc: str) -> None:
    try:
        with get_db_context() as (conn, cur):
            cur.execute("DELETE FROM ClassEnrollments WHERE classId=%s", (id_buoi_hoc,))
            cur.execute("DELETE FROM Classes WHERE id=%s", (id_buoi_hoc,))
            conn.commit()
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise
