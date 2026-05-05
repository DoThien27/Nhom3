"""
Trang Đăng nhập — GymThep Pro System
"""
import threading
import customtkinter as ctk
from database.db_connection import test_connection
import services.user_service as us

ORANGE = "#ea580c"
ORANGE_DARK = "#c2410c"
WHITE = "#ffffff"
BG = "#f1f5f9"
TEXT_PRIMARY = "#0f172a"
TEXT_SECONDARY = "#475569"
TEXT_MUTED = "#94a3b8"
BORDER = "#e2e8f0"
SLATE_50 = "#f1f5f9"
RED = "#dc2626"
EMERALD = "#059669"


class TrangDangNhap(ctk.CTkFrame):
    def __init__(self, master, khi_dang_nhap_thanh_cong, **kwargs):
        super().__init__(master, fg_color=SLATE_50, corner_radius=0, **kwargs)
        self.khi_dang_nhap_thanh_cong = khi_dang_nhap_thanh_cong
        self._tao_giao_dien()

    def _tao_giao_dien(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Center card
        card = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=28,
                             border_width=1, border_color=BORDER,
                             width=440, height=580)
        card.grid(row=0, column=0)
        card.pack_propagate(False)

        # Logo
        logo_frame = ctk.CTkFrame(card, fg_color="#fff7ed", corner_radius=20,
                                   width=80, height=80)
        logo_frame.pack(pady=(44, 0))
        logo_frame.pack_propagate(False)
        ctk.CTkLabel(logo_frame, text="🏆",
                     font=ctk.CTkFont(size=36)).pack(expand=True)

        ctk.CTkLabel(card, text="CLB Thể Thao",
                     font=ctk.CTkFont(family="Inter", size=26, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(pady=(16, 0))
        ctk.CTkLabel(card, text="HỆ THỐNG QUẢN LÝ CÂU LẠC BỘ THỂ THAO",
                     font=ctk.CTkFont(size=9, weight="bold"),
                     text_color=ORANGE).pack()

        # Connection status
        self.nhan_ket_noi = ctk.CTkLabel(card, text="● Đang kết nối...",
                                       font=ctk.CTkFont(size=10, weight="bold"),
                                       text_color=TEXT_MUTED)
        self.nhan_ket_noi.pack(pady=(8, 0))

        # Form
        form = ctk.CTkFrame(card, fg_color=WHITE, corner_radius=0)
        form.pack(fill="x", padx=40, pady=24)

        ctk.CTkLabel(form, text="Tên đăng nhập",
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=TEXT_MUTED, anchor="w").pack(fill="x", pady=(0, 4))
        self.o_nhap_ten_dang_nhap = ctk.CTkEntry(
            form, placeholder_text="Nhập tên đăng nhập...",
            height=46, corner_radius=12, border_color=BORDER,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=SLATE_50, text_color=TEXT_PRIMARY,
            border_width=1
        )
        self.o_nhap_ten_dang_nhap.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(form, text="Mật khẩu",
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=TEXT_MUTED, anchor="w").pack(fill="x", pady=(0, 4))
        self.o_nhap_mat_khau = ctk.CTkEntry(
            form, placeholder_text="Nhập mật khẩu...",
            show="●", height=46, corner_radius=12, border_color=BORDER,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=SLATE_50, text_color=TEXT_PRIMARY,
            border_width=1
        )
        self.o_nhap_mat_khau.pack(fill="x", pady=(0, 4))

        self.nhan_loi = ctk.CTkLabel(form, text="",
                                       font=ctk.CTkFont(size=11),
                                       text_color=RED)
        self.nhan_loi.pack(fill="x", pady=(4, 0))

        self.nut_dang_nhap = ctk.CTkButton(
            form, text="ĐĂNG NHẬP",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=50, corner_radius=14,
            fg_color=ORANGE, hover_color=ORANGE_DARK,
            text_color=WHITE,
            command=self._thuc_hien_dang_nhap
        )
        self.nut_dang_nhap.pack(fill="x", pady=(24, 0))

        # Footer
        ctk.CTkLabel(card, text="© 2025 Hệ Thống Quản Lý Câu Lạc Bộ Thể Thao",
                     font=ctk.CTkFont(size=10), text_color=TEXT_MUTED).pack(pady=(0, 32))

        # Bind Enter key
        self.o_nhap_mat_khau.bind("<Return>", lambda e: self._thuc_hien_dang_nhap())
        self.o_nhap_ten_dang_nhap.bind("<Return>", lambda e: self.o_nhap_mat_khau.focus())

        # Check connection
        self.after(200, self._kiem_tra_ket_noi)

    def _kiem_tra_ket_noi(self):
        """Kiểm tra kết nối DB trong background thread — không block UI."""
        def _check():
            ok = test_connection()
            # Cập nhật label trên main thread
            if ok:
                self.after(0, lambda: self.nhan_ket_noi.configure(
                    text="● Đã kết nối MySQL (XAMPP)", text_color=EMERALD))
            else:
                self.after(0, lambda: self.nhan_ket_noi.configure(
                    text="● Không thể kết nối MySQL (XAMPP)", text_color=RED))
        threading.Thread(target=_check, daemon=True).start()

    def _thuc_hien_dang_nhap(self):
        ten_dang_nhap = self.o_nhap_ten_dang_nhap.get().strip()
        mat_khau = self.o_nhap_mat_khau.get().strip()

        if not ten_dang_nhap or not mat_khau:
            self.nhan_loi.configure(text="Vui lòng nhập đầy đủ thông tin")
            return

        self.nut_dang_nhap.configure(state="disabled", text="Đang đăng nhập...")
        self.nhan_loi.configure(text="")
        self.after(100, lambda: self._thu_dang_nhap(ten_dang_nhap, mat_khau))

    def _thu_dang_nhap(self, ten_dang_nhap, mat_khau):
        """Chạy query trong background thread, cập nhật UI vía after()."""
        def _worker():
            try:
                nguoi_dung = us.dang_nhap(ten_dang_nhap, mat_khau)
                if nguoi_dung:
                    self.after(0, lambda: self.khi_dang_nhap_thanh_cong(nguoi_dung))
                else:
                    self.after(0, lambda: [
                        self.nhan_loi.configure(text="Sai tên đăng nhập hoặc mật khẩu"),
                        self.nut_dang_nhap.configure(state="normal", text="ĐĂNG NHẬP")
                    ])
            except Exception as e:
                self.after(0, lambda err=e: [
                    self.nhan_loi.configure(text=f"Lỗi kết nối: {err}"),
                    self.nut_dang_nhap.configure(state="normal", text="ĐĂNG NHẬP")
                ])
        threading.Thread(target=_worker, daemon=True).start()
