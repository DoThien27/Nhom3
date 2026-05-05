"""
Validators — Bộ kiểm tra dữ liệu đầu vào dùng chung cho toàn hệ thống
"""
import re
import hashlib
from datetime import datetime


def bam_mat_khau(mat_khau: str) -> str:
    """Băm mật khẩu bằng SHA-256, trả về chuỗi hex."""
    return hashlib.sha256(mat_khau.encode("utf-8")).hexdigest()


def khong_de_trong(gia_tri: str, ten_truong: str = "Trường này") -> str | None:
    """Trả về thông báo lỗi nếu rỗng, None nếu hợp lệ."""
    if not gia_tri or not gia_tri.strip():
        return f"{ten_truong} không được để trống."
    return None


def la_so_dien_thoai(gia_tri: str) -> str | None:
    """Số điện thoại VN: 10 chữ số, bắt đầu bằng 0."""
    v = gia_tri.strip()
    if not v:
        return "Số điện thoại không được để trống."
    if not re.fullmatch(r"0\d{9}", v):
        return "Số điện thoại phải có 10 chữ số và bắt đầu bằng 0."
    return None


def la_email(gia_tri: str) -> str | None:
    """Kiểm tra định dạng email (bỏ qua nếu rỗng)."""
    v = gia_tri.strip()
    if not v:
        return None  # Email không bắt buộc
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", v):
        return "Địa chỉ email không hợp lệ."
    return None


def do_dai_toi_thieu(gia_tri: str, min_len: int, ten_truong: str = "Trường") -> str | None:
    v = gia_tri.strip()
    if len(v) < min_len:
        return f"{ten_truong} phải có ít nhất {min_len} ký tự."
    return None


def khong_co_khoang_trang(gia_tri: str, ten_truong: str = "Trường") -> str | None:
    if " " in gia_tri.strip():
        return f"{ten_truong} không được chứa khoảng trắng."
    return None


def la_so_nguyen_duong(gia_tri: str, ten_truong: str = "Trường") -> str | None:
    v = gia_tri.strip()
    if not v:
        return f"{ten_truong} không được để trống."
    try:
        n = int(v)
        if n <= 0:
            return f"{ten_truong} phải là số nguyên dương (> 0)."
    except ValueError:
        return f"{ten_truong} phải là số nguyên."
    return None


def la_so_khong_am(gia_tri: str, ten_truong: str = "Trường") -> str | None:
    v = gia_tri.strip()
    if not v:
        return None  # Có thể bỏ qua
    try:
        n = float(v.replace(",", "."))
        if n < 0:
            return f"{ten_truong} không được âm."
    except ValueError:
        return f"{ten_truong} phải là số."
    return None


def la_so_thuc_duong(gia_tri: str, ten_truong: str = "Trường") -> str | None:
    v = gia_tri.strip()
    if not v:
        return f"{ten_truong} không được để trống."
    try:
        n = float(v.replace(",", "."))
        if n <= 0:
            return f"{ten_truong} phải lớn hơn 0."
    except ValueError:
        return f"{ten_truong} phải là số."
    return None


def dinh_dang_ngay(gia_tri: str) -> str | None:
    """Kiểm tra định dạng YYYY-MM-DD."""
    v = gia_tri.strip()
    if not v:
        return "Ngày không được để trống."
    try:
        datetime.strptime(v, "%Y-%m-%d")
    except ValueError:
        return "Ngày phải theo định dạng YYYY-MM-DD (VD: 2024-12-31)."
    return None


def dinh_dang_gio(gia_tri: str) -> str | None:
    """Kiểm tra định dạng HH:MM."""
    v = gia_tri.strip()
    if not v:
        return "Giờ không được để trống."
    if not re.fullmatch(r"\d{2}:\d{2}", v):
        return "Giờ phải theo định dạng HH:MM (VD: 08:00)."
    h, m = v.split(":")
    if not (0 <= int(h) <= 23 and 0 <= int(m) <= 59):
        return "Giờ không hợp lệ (00:00 - 23:59)."
    return None


def kiem_tra_tat_ca(cac_loi: list) -> list:
    """Lọc bỏ None và trả về danh sách lỗi."""
    return [l for l in cac_loi if l is not None]
