from dataclasses import dataclass, field
from typing import Optional, List, Literal

VaiTro = Literal["ADMIN", "MANAGER", "RECEPTIONIST", "PT", "MEMBER"]
TrangThaiHoiVien = Literal["ACTIVE", "EXPIRED", "PENDING"]
LoaiGoiTap = Literal["MEMBERSHIP", "CLASS", "PT"]
LoaiKhoanThu = Literal["MEMBERSHIP", "CLASS", "FACILITY", "EVENT", "OTHER"]
TrangThaiHoaDon = Literal["UNPAID", "PARTIAL", "PAID", "CANCELLED"]
PhuongThucThanhToan = Literal["CASH", "BANK_TRANSFER", "CARD", "E_WALLET", "OTHER"]


@dataclass
class NguoiDung:
    id: str
    ten_dang_nhap: str
    ho_ten: str
    vai_tro: VaiTro
    mat_khau: Optional[str] = None
    chuyen_mon: Optional[str] = None
    hoc_vien_dang_theo: int = 0
    so_dien_thoai: Optional[str] = None
    dia_chi: Optional[str] = None
    cmnd_cccd: Optional[str] = None


@dataclass
class HoiVien:
    id: str
    ho_ten: str
    so_dien_thoai: str
    email: str
    ngay_gia_nhap: str
    trang_thai: TrangThaiHoiVien = "ACTIVE"
    id_goi_tap_hien_tai: Optional[str] = None
    ten_goi_tap_hien_tai: Optional[str] = None
    ngay_het_han: Optional[str] = None
    so_buoi_con_lai: Optional[int] = None
    id_pt_phu_trach: Optional[str] = None
    ten_pt_phu_trach: Optional[str] = None
    can_nang: float = 0.0
    ten_dang_nhap: Optional[str] = None
    mat_khau: Optional[str] = None
    que_quan: Optional[str] = None


@dataclass
class GoiTap:
    id: str
    ten: str
    loai: LoaiGoiTap
    gia: float
    mo_ta: str
    thoi_han_thang: Optional[int] = None
    so_buoi: Optional[int] = None


@dataclass
class BuoiHoc:
    id: str
    ten: str
    id_hlv: str
    gio: str
    thu_trong_tuan: str
    suc_chua: int
    gia: float = 0.0
    danh_sach_id_hoi_vien: List[str] = field(default_factory=list)




@dataclass
class ChiTietHoaDon:
    ten: str                                    # item_name
    so_luong: int                               # quantity
    gia: float                                  # unit_price
    loai_khoan_thu: str = "OTHER"               # item_type: MEMBERSHIP/CLASS/FACILITY/EVENT/OTHER
    id_tham_chieu: Optional[str] = None         # reference_id (plan_id, class_id, ...)
    giam_gia_dong: float = 0.0                  # discount per line
    thanh_tien: float = 0.0                     # line_total = qty*gia - giam_gia_dong
    ghi_chu: str = ""                           # item_note


@dataclass
class HoaDon:
    id: str
    id_hoi_vien: str
    danh_sach_muc: List[ChiTietHoaDon]
    tong_tien: float                            # total_amount (sum of line_totals)
    ngay: str                                   # invoice_date
    phuong_thuc: str                            # payment_method
    giam_gia: float = 0.0                       # discount_amount (invoice-level)
    thanh_tien: float = 0.0                     # final_amount = tong_tien - giam_gia
    da_tra: float = 0.0                         # paid_amount
    con_lai: float = 0.0                        # remaining_amount = thanh_tien - da_tra
    trang_thai_thanh_toan: str = "UNPAID"       # payment_status
    ghi_chu: str = ""                           # note
    nguoi_tao: str = ""                         # created_by


@dataclass
class SuKien:
    id: str
    ten: str
    mo_ta: str
    ngay: str
    gio: str
    dia_diem: str
    suc_chua: int
    gia: float = 0.0
    trang_thai: str = "UPCOMING"


@dataclass
class NguoiThamGiaSuKien:
    id: str
    id_su_kien: str
    id_hoi_vien: str
    ten_hoi_vien: str
    ngay_dang_ky: str
    trang_thai: str = "PENDING"
