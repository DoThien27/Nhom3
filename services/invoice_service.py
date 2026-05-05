"""
invoice_service.py — Dịch vụ Hóa đơn/Thanh toán đa dịch vụ
CLB Thể Thao — Hỗ trợ: MEMBERSHIP, CLASS, FACILITY, EVENT, OTHER
"""
from typing import List, Optional, Dict, Any
from database.db_connection import get_db_context
from utils.logger import logger
from models.models import HoaDon, ChiTietHoaDon

# ─────────────────────────── CONSTANTS ───────────────────────────

LOAI_KHOAN_THU_VI = {
    "MEMBERSHIP": "Gói hội viên",
    "CLASS":      "Lớp/Buổi tập",
    "FACILITY":   "Sân bãi/Phòng tập",
    "EVENT":      "Sự kiện/Giải đấu",
    "OTHER":      "Khác",
}

PHUONG_THUC_VI = {
    "CASH":          "Tiền mặt",
    "BANK_TRANSFER": "Chuyển khoản",
    "CARD":          "Thẻ",
    "E_WALLET":      "Ví điện tử",
    "OTHER":         "Khác",
    # Legacy values
    "TRANSFER":      "Chuyển khoản",
    "E-WALLET":      "Ví điện tử",
}

TRANG_THAI_HD_VI = {
    "UNPAID":    "Chưa thanh toán",
    "PARTIAL":   "Thanh toán một phần",
    "PAID":      "Đã thanh toán",
    "CANCELLED": "Đã hủy",
}


# ─────────────────────────── HELPERS ───────────────────────────

def _tinh_trang_thai(da_tra: float, thanh_tien: float) -> str:
    """Tự động tính trạng thái thanh toán."""
    if thanh_tien <= 0:
        return "PAID" if da_tra >= 0 else "UNPAID"
    if da_tra <= 0:
        return "UNPAID"
    if da_tra >= thanh_tien:
        return "PAID"
    return "PARTIAL"


def tinh_tong(
    items: List[ChiTietHoaDon],
    giam_gia_hd: float = 0.0,
    da_tra: float = 0.0
) -> Dict[str, Any]:
    """Tính toán các trường tổng hợp của hóa đơn."""
    tong = sum(it.thanh_tien for it in items)
    thanh_tien = max(0.0, tong - giam_gia_hd)
    con_lai = max(0.0, thanh_tien - da_tra)
    trang_thai = _tinh_trang_thai(da_tra, thanh_tien)
    return {
        "tong_tien": tong,
        "giam_gia": giam_gia_hd,
        "thanh_tien": thanh_tien,
        "da_tra": da_tra,
        "con_lai": con_lai,
        "trang_thai_thanh_toan": trang_thai,
    }


def _row_to_hoadon(row) -> HoaDon:
    return HoaDon(
        id=str(row.id),
        id_hoi_vien=str(row.memberId),
        danh_sach_muc=[],
        tong_tien=float(row.total or 0),
        ngay=str(row.date) if row.date else "",
        phuong_thuc=row.method or "CASH",
        giam_gia=float(row.discount_amount or 0),
        thanh_tien=float(row.final_amount or 0),
        da_tra=float(row.paid_amount or 0),
        con_lai=float(row.remaining_amount or 0),
        trang_thai_thanh_toan=row.payment_status or "UNPAID",
        ghi_chu=row.note or "",
        nguoi_tao=row.created_by or "",
    )


def _row_to_chitiet(row) -> ChiTietHoaDon:
    return ChiTietHoaDon(
        ten=row.item_name or "",
        so_luong=int(row.quantity or 1),
        gia=float(row.unit_price or 0),
        loai_khoan_thu=row.item_type or "OTHER",
        id_tham_chieu=str(row.reference_id) if row.reference_id else None,
        giam_gia_dong=float(row.discount_amount or 0),
        thanh_tien=float(row.line_total or 0),
        ghi_chu=row.item_note or "",
    )


# ─────────────────────────── READ ───────────────────────────

def lay_tat_ca() -> List[HoaDon]:
    """Lấy tất cả hóa đơn (không kèm chi tiết dòng)."""
    try:
        with get_db_context() as (conn, cur):
            cur.execute(
                "SELECT i.*, m.fullName AS ten_hoi_vien "
                "FROM Invoices i LEFT JOIN Members m ON i.memberId = m.id "
                "ORDER BY i.date DESC"
            )
            rows = cur.fetchall()
            result = []
            for row in rows:
                hd = _row_to_hoadon(row)
                # Gắn tên hội viên vào ghi_chu tạm để UI dùng (không làm phức tạp model)
                hd._ten_hoi_vien = getattr(row, "ten_hoi_vien", "") or ""
                result.append(hd)
            return result
    except Exception as e:
        logger.error(f"[invoice_service] lay_tat_ca ERROR: {e}")
        raise


def lay_theo_id(id_hoa_don: str) -> Optional[HoaDon]:
    """Lấy một hóa đơn kèm chi tiết dòng."""
    try:
        with get_db_context() as (conn, cur):
            cur.execute("SELECT * FROM Invoices WHERE id=%s", (id_hoa_don,))
            row = cur.fetchone()
            if not row:
                return None
            hd = _row_to_hoadon(row)
            hd.danh_sach_muc = lay_cac_khoan(id_hoa_don)
            return hd
    except Exception as e:
        logger.error(f"[invoice_service] lay_theo_id ERROR: {e}")
        raise


def lay_cac_khoan(id_hoa_don: str) -> List[ChiTietHoaDon]:
    """Lấy danh sách dòng chi tiết của một hóa đơn."""
    try:
        with get_db_context() as (conn, cur):
            cur.execute(
                "SELECT * FROM InvoiceItems WHERE invoiceId=%s ORDER BY id",
                (id_hoa_don,)
            )
            return [_row_to_chitiet(r) for r in cur.fetchall()]
    except Exception as e:
        logger.error(f"[invoice_service] lay_cac_khoan ERROR: {e}")
        return []


def lay_chua_thanh_toan() -> List[HoaDon]:
    """Lấy các hóa đơn chưa/chưa đủ thanh toán."""
    try:
        with get_db_context() as (conn, cur):
            cur.execute(
                "SELECT i.*, m.fullName AS ten_hoi_vien FROM Invoices i "
                "LEFT JOIN Members m ON i.memberId = m.id "
                "WHERE i.payment_status IN ('UNPAID','PARTIAL') "
                "ORDER BY i.date DESC"
            )
            result = []
            for row in cur.fetchall():
                hd = _row_to_hoadon(row)
                hd._ten_hoi_vien = getattr(row, "ten_hoi_vien", "") or ""
                result.append(hd)
            return result
    except Exception as e:
        logger.error(f"[invoice_service] lay_chua_thanh_toan ERROR: {e}")
        return []


# ─────────────────────────── CREATE ───────────────────────────

def tao(
    id_hoa_don: str,
    id_hoi_vien: str,
    items: List[ChiTietHoaDon],
    giam_gia_hd: float = 0.0,
    da_tra: float = 0.0,
    phuong_thuc: str = "CASH",
    ghi_chu: str = "",
    nguoi_tao: str = "",
    ngay: str = "",
) -> HoaDon:
    """
    Tạo hóa đơn mới với nhiều dòng chi tiết.
    Các mục thanh toán được thêm vào InvoiceItems.
    Dùng transaction — rollback toàn bộ nếu lỗi.
    """
    # ── Validation ──
    if not id_hoi_vien:
        raise ValueError("Phải chọn hội viên.")
    if not items:
        raise ValueError("Hóa đơn phải có ít nhất một dòng chi tiết.")
    for it in items:
        if it.so_luong <= 0:
            raise ValueError(f"Số lượng của '{it.ten}' phải lớn hơn 0.")
        if it.gia < 0:
            raise ValueError(f"Đơn giá của '{it.ten}' không được âm.")
        if it.giam_gia_dong < 0:
            raise ValueError(f"Giảm giá dòng của '{it.ten}' không được âm.")
    if giam_gia_hd < 0:
        raise ValueError("Giảm giá hóa đơn không được âm.")

    # ── Tính toán tổng ──
    for it in items:
        it.thanh_tien = round(it.so_luong * it.gia - it.giam_gia_dong, 2)

    from datetime import datetime
    totals = tinh_tong(items, giam_gia_hd, da_tra)
    ngay_hd = ngay or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    hd = HoaDon(
        id=id_hoa_don,
        id_hoi_vien=id_hoi_vien,
        danh_sach_muc=items,
        tong_tien=totals["tong_tien"],
        ngay=ngay_hd,
        phuong_thuc=phuong_thuc,
        giam_gia=giam_gia_hd,
        thanh_tien=totals["thanh_tien"],
        da_tra=totals["da_tra"],
        con_lai=totals["con_lai"],
        trang_thai_thanh_toan=totals["trang_thai_thanh_toan"],
        ghi_chu=ghi_chu,
        nguoi_tao=nguoi_tao,
    )

    try:
        with get_db_context() as (conn, cur):
            # Lưu hóa đơn
            cur.execute(
                "INSERT INTO Invoices (id, memberId, total, discount_amount, final_amount, "
                "paid_amount, remaining_amount, date, method, payment_status, note, created_by) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                    hd.id, hd.id_hoi_vien, hd.tong_tien, hd.giam_gia,
                    hd.thanh_tien, hd.da_tra, hd.con_lai,
                    ngay_hd, hd.phuong_thuc, hd.trang_thai_thanh_toan,
                    hd.ghi_chu, hd.nguoi_tao,
                )
            )

            # Lưu chi tiết dòng và trừ kho
            for it in items:
                cur.execute(
                    "INSERT INTO InvoiceItems (invoiceId, item_type, reference_id, item_name, "
                    "quantity, unit_price, discount_amount, line_total, item_note) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (
                        hd.id, it.loai_khoan_thu, it.id_tham_chieu,
                        it.ten, it.so_luong, it.gia,
                        it.giam_gia_dong, it.thanh_tien, it.ghi_chu,
                    )
                )

            conn.commit()
            logger.info(f"[invoice_service] Tao HĐ {hd.id} thanh cong.")
    except Exception as e:
        logger.error(f"[invoice_service] tao ERROR: {e}")
        raise

    return hd


# ─────────────────────────── UPDATE ───────────────────────────

def cap_nhat_thanh_toan(
    id_hoa_don: str,
    da_tra_them: float,
    phuong_thuc: str = "",
    ghi_chu: str = "",
) -> HoaDon:
    """Cập nhật số tiền đã trả thêm, tự tính lại trạng thái."""
    try:
        with get_db_context() as (conn, cur):
            cur.execute("SELECT * FROM Invoices WHERE id=%s", (id_hoa_don,))
            row = cur.fetchone()
            if not row:
                raise ValueError(f"Không tìm thấy hóa đơn {id_hoa_don}.")
            if row.payment_status == "CANCELLED":
                raise ValueError("Hóa đơn đã bị hủy, không thể cập nhật thanh toán.")

            new_paid = float(row.paid_amount or 0) + da_tra_them
            final    = float(row.final_amount or 0)
            new_remaining = max(0.0, final - new_paid)
            new_status = _tinh_trang_thai(new_paid, final)
            pm = phuong_thuc or row.method
            note = ghi_chu or (row.note or "")

            cur.execute(
                "UPDATE Invoices SET paid_amount=%s, remaining_amount=%s, "
                "payment_status=%s, method=%s, note=%s WHERE id=%s",
                (new_paid, new_remaining, new_status, pm, note, id_hoa_don)
            )
            conn.commit()

        return lay_theo_id(id_hoa_don)
    except Exception as e:
        logger.error(f"[invoice_service] cap_nhat_thanh_toan ERROR: {e}")
        raise


def huy(id_hoa_don: str) -> None:
    """Hủy hóa đơn — đặt trạng thái CANCELLED."""
    try:
        with get_db_context() as (conn, cur):
            cur.execute("SELECT payment_status FROM Invoices WHERE id=%s", (id_hoa_don,))
            row = cur.fetchone()
            if not row:
                raise ValueError(f"Không tìm thấy hóa đơn {id_hoa_don}.")
            if row.payment_status == "PAID":
                raise ValueError("Hóa đơn đã thanh toán đủ, không thể hủy.")
            if row.payment_status == "CANCELLED":
                raise ValueError("Hóa đơn đã bị hủy trước đó.")

            cur.execute(
                "UPDATE Invoices SET payment_status='CANCELLED' WHERE id=%s",
                (id_hoa_don,)
            )
            conn.commit()
            logger.info(f"[invoice_service] Huy HĐ {id_hoa_don} thanh cong.")
    except Exception as e:
        logger.error(f"[invoice_service] huy ERROR: {e}")
        raise


def xoa(id_hoa_don: str) -> None:
    """Xóa hóa đơn và tất cả dòng chi tiết."""
    try:
        with get_db_context() as (conn, cur):
            cur.execute("DELETE FROM InvoiceItems WHERE invoiceId=%s", (id_hoa_don,))
            cur.execute("DELETE FROM Invoices WHERE id=%s", (id_hoa_don,))
            conn.commit()
    except Exception as e:
        logger.error(f"[invoice_service] xoa ERROR: {e}")
        raise


# ─────────────────────────── STATISTICS ───────────────────────────

def thong_ke_theo_thang(nam: int, thang: int) -> dict:
    """Thống kê doanh thu (paid_amount) theo tháng."""
    try:
        with get_db_context() as (conn, cur):
            cur.execute(
                "SELECT SUM(paid_amount) AS tong, SUM(remaining_amount) AS con_no, "
                "COUNT(*) AS so_hd FROM Invoices "
                "WHERE YEAR(date)=%s AND MONTH(date)=%s AND payment_status != 'CANCELLED'",
                (nam, thang)
            )
            row = cur.fetchone()
            return {
                "tong_doanh_thu": float(row.tong or 0),
                "con_no":         float(row.con_no or 0),
                "so_hoa_don":     int(row.so_hd or 0),
            }
    except Exception as e:
        logger.error(f"[invoice_service] thong_ke_theo_thang ERROR: {e}")
        return {"tong_doanh_thu": 0, "con_no": 0, "so_hoa_don": 0}


def thong_ke_doanh_thu() -> dict:
    """Thống kê tổng quan doanh thu."""
    try:
        with get_db_context() as (conn, cur):
            cur.execute(
                "SELECT SUM(paid_amount) AS da_thu, SUM(remaining_amount) AS con_no, "
                "SUM(final_amount) AS thanh_tien, COUNT(*) AS so_hd "
                "FROM Invoices WHERE payment_status != 'CANCELLED'"
            )
            row = cur.fetchone()
            # Doanh thu theo loại khoản thu
            cur.execute(
                "SELECT ii.item_type, SUM(ii.line_total) AS tong "
                "FROM InvoiceItems ii "
                "JOIN Invoices i ON ii.invoiceId = i.id "
                "WHERE i.payment_status != 'CANCELLED' "
                "GROUP BY ii.item_type"
            )
            theo_loai = {r.item_type: float(r.tong or 0) for r in cur.fetchall()}
            return {
                "da_thu":     float(row.da_thu or 0),
                "con_no":     float(row.con_no or 0),
                "thanh_tien": float(row.thanh_tien or 0),
                "so_hoa_don": int(row.so_hd or 0),
                "theo_loai":  theo_loai,
            }
    except Exception as e:
        logger.error(f"[invoice_service] thong_ke_doanh_thu ERROR: {e}")
        return {"da_thu": 0, "con_no": 0, "thanh_tien": 0, "so_hoa_don": 0, "theo_loai": {}}


def doanh_thu_theo_thang_12() -> List[float]:
    """Trả về list 12 phần tử — doanh thu paid_amount theo từng tháng trong năm hiện tại."""
    from datetime import datetime
    nam = datetime.now().year
    try:
        with get_db_context() as (conn, cur):
            cur.execute(
                "SELECT MONTH(date) AS thang, SUM(paid_amount) AS tong "
                "FROM Invoices "
                "WHERE YEAR(date)=%s AND payment_status != 'CANCELLED' "
                "GROUP BY MONTH(date)",
                (nam,)
            )
            data = {int(r.thang): float(r.tong or 0) for r in cur.fetchall()}
            return [data.get(m, 0.0) for m in range(1, 13)]
    except Exception as e:
        logger.error(f"[invoice_service] doanh_thu_theo_thang_12 ERROR: {e}")
        return [0.0] * 12
