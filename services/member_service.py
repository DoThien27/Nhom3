from typing import List
from database.db_connection import get_db_context
from utils.logger import logger
from models.models import HoiVien


def lay_tat_ca() -> List[HoiVien]:
    try:
        with get_db_context() as (conn, cur):
            cur.execute("""
                SELECT m.*, p.name as activePlanName, u.fullName as assignedPTName
                FROM Members m
                LEFT JOIN Plans p ON m.activePlanId = p.id
                LEFT JOIN Users u ON m.assignedPTId = u.id
            """)
            members = []
            for row in cur.fetchall():
                members.append(HoiVien(
                    id=str(row.id),
                    ho_ten=row.fullName or "",
                    so_dien_thoai=row.phone or "",
                    email=row.email or "",
                    ngay_gia_nhap=str(row.joinDate) if row.joinDate else "",
                    trang_thai=row.status or "ACTIVE",
                    id_goi_tap_hien_tai=row.activePlanId,
                    ten_goi_tap_hien_tai=row.activePlanName,
                    ngay_het_han=str(row.expiryDate) if row.expiryDate else None,
                    id_pt_phu_trach=row.assignedPTId,
                    ten_pt_phu_trach=row.assignedPTName,
                    can_nang=float(row.weight) if row.weight else 0.0,
                    ten_dang_nhap=row.username,
                    mat_khau=row.password,
                    que_quan=row.homeTown if row.homeTown else None,
                ))
            return members
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise

def dem_tong(keyword: str = "", filters: dict = None) -> int:
    try:
        with get_db_context() as (conn, cur):
            query = "SELECT COUNT(*) as c FROM Members m WHERE 1=1"
            params = []
            if keyword:
                query += " AND (m.fullName LIKE %s OR m.phone LIKE %s)"
                params.extend([f"%{keyword}%", f"%{keyword}%"])
            if filters and filters.get('status') and filters['status'] != 'Tất cả':
                # Convert Vietnamese status back to Enum if needed, or filter handles it
                status_map = {"Hoạt động": "ACTIVE", "Hết hạn": "EXPIRED", "Chờ duyệt": "PENDING"}
                status = status_map.get(filters['status'], filters['status'])
                query += " AND m.status = %s"
                params.append(status)
                
            cur.execute(query, params)
            return cur.fetchone()['c'] or 0
    except Exception as e:
        logger.error(f"Database error: {e}")
        return 0

def lay_phan_trang(page: int, page_size: int, keyword: str = "", filters: dict = None) -> List[HoiVien]:
    try:
        with get_db_context() as (conn, cur):
            query = """
                SELECT m.*, p.name as activePlanName, u.fullName as assignedPTName
                FROM Members m
                LEFT JOIN Plans p ON m.activePlanId = p.id
                LEFT JOIN Users u ON m.assignedPTId = u.id
                WHERE 1=1
            """
            params = []
            if keyword:
                query += " AND (m.fullName LIKE %s OR m.phone LIKE %s)"
                params.extend([f"%{keyword}%", f"%{keyword}%"])
            if filters and filters.get('status') and filters['status'] != 'Tất cả':
                status_map = {"Hoạt động": "ACTIVE", "Hết hạn": "EXPIRED", "Chờ duyệt": "PENDING"}
                status = status_map.get(filters['status'], filters['status'])
                query += " AND m.status = %s"
                params.append(status)
                
            query += " ORDER BY m.joinDate DESC LIMIT %s OFFSET %s"
            params.extend([page_size, (page - 1) * page_size])
            
            cur.execute(query, params)
            members = []
            for row in cur.fetchall():
                members.append(HoiVien(
                    id=str(row.id),
                    ho_ten=row.fullName or "",
                    so_dien_thoai=row.phone or "",
                    email=row.email or "",
                    ngay_gia_nhap=str(row.joinDate) if row.joinDate else "",
                    trang_thai=row.status or "ACTIVE",
                    id_goi_tap_hien_tai=row.activePlanId,
                    ten_goi_tap_hien_tai=row.activePlanName,
                    ngay_het_han=str(row.expiryDate) if row.expiryDate else None,
                    id_pt_phu_trach=row.assignedPTId,
                    ten_pt_phu_trach=row.assignedPTName,
                    can_nang=float(row.weight) if row.weight else 0.0,
                    ten_dang_nhap=row.username,
                    mat_khau=row.password,
                    que_quan=row.homeTown if row.homeTown else None,
                ))
            return members
    except Exception as e:
        logger.error(f"Database error: {e}")
        return []



def them(hoi_vien: HoiVien) -> HoiVien:
    try:
        with get_db_context() as (conn, cur):
            cur.execute(
                "INSERT INTO Members (id, fullName, phone, email, joinDate, status, weight, "
                "username, password, homeTown) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (hoi_vien.id, hoi_vien.ho_ten, hoi_vien.so_dien_thoai, hoi_vien.email,
                 hoi_vien.ngay_gia_nhap, hoi_vien.trang_thai,
                 hoi_vien.can_nang,
                 hoi_vien.ten_dang_nhap, hoi_vien.mat_khau,
                 hoi_vien.que_quan)
            )
            conn.commit()
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise
    return hoi_vien


def cap_nhat(hoi_vien: HoiVien) -> HoiVien:
    try:
        with get_db_context() as (conn, cur):
            cur.execute("""
                UPDATE Members SET
                    fullName=%s, phone=%s, email=%s, status=%s,
                    weight=%s,
                    activePlanId=%s, expiryDate=%s, assignedPTId=%s,
                    username=%s, homeTown=%s
                WHERE id=%s
            """,
                (hoi_vien.ho_ten, hoi_vien.so_dien_thoai, hoi_vien.email, hoi_vien.trang_thai,
                 hoi_vien.can_nang,
                 hoi_vien.id_goi_tap_hien_tai, hoi_vien.ngay_het_han, hoi_vien.id_pt_phu_trach,
                 hoi_vien.ten_dang_nhap, hoi_vien.que_quan, hoi_vien.id)
            )
            if hoi_vien.mat_khau:
                cur.execute("UPDATE Members SET password=%s WHERE id=%s",
                            (hoi_vien.mat_khau, hoi_vien.id))
            conn.commit()
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise
    return hoi_vien


def xoa(id_hoi_vien: str) -> None:
    try:
        with get_db_context() as (conn, cur):
            cur.execute("DELETE FROM Members WHERE id=%s", (id_hoi_vien,))
            conn.commit()
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise


def id_hlv(id_hlv_: str) -> List[HoiVien]:
    """Lấy danh sách hội viên được phân công cho HLV"""
    try:
        with get_db_context() as (conn, cur):
            cur.execute("""
                SELECT m.* FROM Members m WHERE m.assignedPTId=%s
            """, (id_hlv_,))
            members = []
            for row in cur.fetchall():
                members.append(HoiVien(
                    id=str(row.id),
                    ho_ten=row.fullName or "",
                    so_dien_thoai=row.phone or "",
                    email=row.email or "",
                    ngay_gia_nhap=str(row.joinDate) if row.joinDate else "",
                    trang_thai=row.status or "ACTIVE",
                    can_nang=float(row.weight) if row.weight else 0.0,
                    ten_dang_nhap=row.username,
                    que_quan=row.homeTown if row.homeTown else None,
                ))
            return members
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise
