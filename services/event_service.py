import traceback
from typing import List
from database.db_connection import get_db_context
from utils.logger import logger
from models.models import SuKien, NguoiThamGiaSuKien


# ─── Sự Kiện ────────────────────────────────────────────────────────────────

def lay_tat_ca_su_kien() -> List[SuKien]:
    try:
        with get_db_context() as (conn, cur):
            cur.execute("SELECT * FROM Events ORDER BY date DESC, time DESC")
            records = []
            for row in cur.fetchall():
                records.append(SuKien(
                    id=str(row.id),
                    ten=row.name or "",
                    mo_ta=row.description or "",
                    ngay=str(row.date) if row.date else "",
                    gio=str(row.time) if row.time else "",
                    dia_diem=row.location or "",
                    suc_chua=int(row.capacity) if row.capacity else 0,
                    gia=float(row.price) if row.price else 0.0,
                    trang_thai=row.status or "UPCOMING",
                ))
            return records
    except Exception as e:
        logger.error(f"[event_service] lay_tat_ca_su_kien ERROR: {e}")
        traceback.print_exc()
        return []


def them_su_kien(su_kien: SuKien) -> SuKien:
    try:
        with get_db_context() as (conn, cur):
            cur.execute(
                "INSERT INTO Events (id, name, description, date, time, location, capacity, price, status) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (su_kien.id, su_kien.ten, su_kien.mo_ta, su_kien.ngay, su_kien.gio,
                 su_kien.dia_diem, su_kien.suc_chua, su_kien.gia, su_kien.trang_thai),
            )
            conn.commit()
            logger.info(f"[event_service] them_su_kien OK: id={su_kien.id}")
            return su_kien
    except Exception as e:
        logger.error(f"[event_service] them_su_kien ERROR: {e}")
        traceback.print_exc()
        raise


def cap_nhat_su_kien(su_kien: SuKien) -> SuKien:
    try:
        with get_db_context() as (conn, cur):
            cur.execute(
                "UPDATE Events SET name=%s, description=%s, date=%s, time=%s, "
                "location=%s, capacity=%s, price=%s, status=%s WHERE id=%s",
                (su_kien.ten, su_kien.mo_ta, su_kien.ngay, su_kien.gio,
                 su_kien.dia_diem, su_kien.suc_chua, su_kien.gia, su_kien.trang_thai, su_kien.id),
            )
            conn.commit()
            logger.info(f"[event_service] cap_nhat_su_kien OK: id={su_kien.id}")
            return su_kien
    except Exception as e:
        logger.error(f"[event_service] cap_nhat_su_kien ERROR: {e}")
        traceback.print_exc()
        raise


def xoa_su_kien(id_su_kien: str) -> bool:
    try:
        with get_db_context() as (conn, cur):
            cur.execute("DELETE FROM EventParticipants WHERE eventId=%s", (id_su_kien,))
            cur.execute("DELETE FROM Events WHERE id=%s", (id_su_kien,))
            conn.commit()
            logger.info(f"[event_service] xoa_su_kien OK: id={id_su_kien}")
            return True
    except Exception as e:
        logger.error(f"[event_service] xoa_su_kien ERROR: {e}")
        traceback.print_exc()
        return False


# ─── Người Tham Gia ──────────────────────────────────────────────────────────

def lay_nguoi_tham_gia_su_kien(id_su_kien: str) -> List[NguoiThamGiaSuKien]:
    try:
        with get_db_context() as (conn, cur):
            cur.execute(
                "SELECT ep.id, ep.eventId, ep.memberId, ep.memberName, ep.registerDate, ep.status, "
                "m.fullName as tenThucSu "
                "FROM EventParticipants ep "
                "LEFT JOIN Members m ON ep.memberId = m.id "
                "WHERE ep.eventId = %s ORDER BY ep.registerDate DESC",
                (id_su_kien,),
            )
            records = []
            for row in cur.fetchall():
                ten = row.tenThucSu or row.memberName or ""
                records.append(NguoiThamGiaSuKien(
                    id=str(row.id),
                    id_su_kien=str(row.eventId),
                    id_hoi_vien=str(row.memberId),
                    ten_hoi_vien=ten,
                    ngay_dang_ky=str(row.registerDate) if row.registerDate else "",
                    trang_thai=row.status or "PENDING",
                ))
            return records
    except Exception as e:
        logger.error(f"[event_service] lay_nguoi_tham_gia_su_kien ERROR: {e}")
        traceback.print_exc()
        return []


def them_nguoi_tham_gia(nguoi_tham_gia: NguoiThamGiaSuKien) -> NguoiThamGiaSuKien:
    """Thêm người tham gia vào sự kiện. Raise exception nếu lỗi."""
    logger.info(f"[event_service] them_nguoi_tham_gia: id={nguoi_tham_gia.id} "
                f"eventId={nguoi_tham_gia.id_su_kien} memberId={nguoi_tham_gia.id_hoi_vien}")
    try:
        with get_db_context() as (conn, cur):
            cur.execute(
                "INSERT INTO EventParticipants "
                "(id, eventId, memberId, memberName, registerDate, status) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (
                    nguoi_tham_gia.id,
                    nguoi_tham_gia.id_su_kien,
                    nguoi_tham_gia.id_hoi_vien,
                    nguoi_tham_gia.ten_hoi_vien,
                    nguoi_tham_gia.ngay_dang_ky,
                    nguoi_tham_gia.trang_thai,
                ),
            )
            conn.commit()
            logger.info(f"[event_service] them_nguoi_tham_gia OK: id={nguoi_tham_gia.id}")
            return nguoi_tham_gia
    except Exception as e:
        logger.error(f"[event_service] them_nguoi_tham_gia ERROR: {e}")
        traceback.print_exc()
        raise


def cap_nhat_trang_thai_nguoi_tham_gia(id_nguoi_tham_gia: str, trang_thai: str) -> bool:
    try:
        with get_db_context() as (conn, cur):
            cur.execute(
                "UPDATE EventParticipants SET status=%s WHERE id=%s",
                (trang_thai, id_nguoi_tham_gia),
            )
            conn.commit()
            logger.info(f"[event_service] cap_nhat_tt OK: id={id_nguoi_tham_gia} status={trang_thai}")
            return True
    except Exception as e:
        logger.error(f"[event_service] cap_nhat_trang_thai ERROR: {e}")
        traceback.print_exc()
        return False


def xoa_nguoi_tham_gia_su_kien(id_nguoi_tham_gia: str) -> bool:
    try:
        with get_db_context() as (conn, cur):
            cur.execute("DELETE FROM EventParticipants WHERE id=%s", (id_nguoi_tham_gia,))
            conn.commit()
            logger.info(f"[event_service] xoa_nguoi_tham_gia OK: id={id_nguoi_tham_gia}")
            return True
    except Exception as e:
        logger.error(f"[event_service] xoa_nguoi_tham_gia ERROR: {e}")
        traceback.print_exc()
        return False
