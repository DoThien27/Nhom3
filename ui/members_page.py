"""
Quan ly Hoi Vien — Members Page
Chuc nang: Xem danh sach (grid card), Tim kiem, Them, Sua, Xoa
"""
import math
import threading
import customtkinter as ctk
import time
from models.models import HoiVien
import services.member_service as ms
from ui.app import (ORANGE, ORANGE_DARK, ORANGE_LIGHT, WHITE, BG,
                     TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, BORDER, EMERALD, RED, BLUE)


class TrangHoiVien(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, fg_color=BG, corner_radius=0, **kwargs)
        self.app = app
        self.trang_hien_tai = 1
        self.so_luong_moi_trang = 12 # Chia đều cho 1, 2, 3 cột
        self.bien_tim_kiem = ctk.StringVar()
        self.bien_tim_kiem.trace("w", lambda *a: self.app.debounce("member_search", self._dat_lai_trang_va_lam_moi))
        self.filter_var = ctk.StringVar(value="Tất cả")
        self._tao_giao_dien()

    def _tao_giao_dien(self):
        from ui.components import create_page_header, create_pagination
        
        vai_tro = self.app.nguoi_dung_hien_tai.vai_tro
        has_add = vai_tro in ("ADMIN", "MANAGER", "RECEPTIONIST")
        
        self.header_frame, self.search_entry, self.filter_combo = create_page_header(
            self, title="QUẢN LÝ HỘI VIÊN",
            primary_action_text="＋ Thêm mới" if has_add else None,
            primary_action_cmd=self._mo_hop_thoai_them if has_add else None,
            search_placeholder="Tìm tên, SĐT...",
            search_cmd=lambda e: None, # Đã dùng trace
            filter_options=["Tất cả", "Hoạt động", "Chờ duyệt", "Hết hạn"],
            filter_cmd=lambda _: self._dat_lai_trang_va_lam_moi()
        )
        self.search_entry.configure(textvariable=self.bien_tim_kiem)
        self.filter_combo.configure(variable=self.filter_var)

        # Scrollable grid
        self.vung_cuon = ctk.CTkScrollableFrame(self, fg_color=BG, corner_radius=0,
                                              scrollbar_button_color=BORDER)
        self.vung_cuon.pack(fill="both", expand=True, padx=16, pady=0)

        # Container cho phân trang
        self.khung_phan_trang_container = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        self.khung_phan_trang_container.pack(fill="x", padx=16, pady=(0, 16))

        self._lam_moi_danh_sach()

    def _dat_lai_trang_va_lam_moi(self):
        self.trang_hien_tai = 1
        self._lam_moi_danh_sach()

    def _chuyen_trang(self, page_num):
        self.trang_hien_tai = page_num
        self._lam_moi_danh_sach()

    def _lam_moi_danh_sach(self):
        from ui.components import clear_frame, create_pagination, calculate_responsive_columns
        clear_frame(self.vung_cuon)

        tu_tim_kiem = self.bien_tim_kiem.get().strip()
        filters = {"status": self.filter_var.get()}

        def _worker():
            try:
                tong_so = ms.dem_tong(tu_tim_kiem, filters)
                danh_sach = ms.lay_phan_trang(self.trang_hien_tai, self.so_luong_moi_trang, tu_tim_kiem, filters)
            except Exception as e:
                tong_so, danh_sach = 0, []
                print(f"Lỗi: {e}")

            def _cap_nhat_ui():
                if not danh_sach:
                    ctk.CTkLabel(self.vung_cuon, text="Không tìm thấy hội viên nào",
                                 font=ctk.CTkFont(size=13), text_color=TEXT_MUTED).pack(pady=60)
                else:
                    cols = calculate_responsive_columns(self.winfo_width(), max_cols=3, min_width=320)
                    for col in range(cols):
                        self.vung_cuon.grid_columnconfigure(col, weight=1)
                    
                    for i, hoi_vien in enumerate(danh_sach):
                        row = i // cols
                        col = i % cols
                        self._the_hoi_vien(self.vung_cuon, hoi_vien).grid(
                            row=row, column=col, padx=8, pady=8, sticky="nsew"
                        )
                
                # Cập nhật phân trang
                clear_frame(self.khung_phan_trang_container)
                pagination = create_pagination(self.khung_phan_trang_container, self.trang_hien_tai, tong_so, self.so_luong_moi_trang, self._chuyen_trang)
                pagination.pack(fill="x")

            self.after(0, _cap_nhat_ui)

        threading.Thread(target=_worker, daemon=True).start()



    def _the_hoi_vien(self, cha, hoi_vien: HoiVien):
        card = ctk.CTkFrame(cha, fg_color=WHITE, corner_radius=20,
                             border_width=1, border_color=BORDER)

        # Avatar + name row
        tren = ctk.CTkFrame(card, fg_color=WHITE, corner_radius=0)
        tren.pack(fill="x", padx=20, pady=(20, 0))

        chu_cai_dau = "".join(w[0] for w in hoi_vien.ho_ten.split() if w)[-1:].upper()
        avatar = ctk.CTkLabel(tren, text=chu_cai_dau,
                               font=ctk.CTkFont(size=22, weight="bold"),
                               fg_color="#fed7aa", text_color=ORANGE,
                               corner_radius=12, width=56, height=56)
        avatar.pack(side="left")

        info = ctk.CTkFrame(tren, fg_color=WHITE, corner_radius=0)
        info.pack(side="left", padx=(12, 0), fill="both", expand=True)
        ctk.CTkLabel(info, text=hoi_vien.ho_ten.upper(),
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT_PRIMARY, anchor="w").pack(anchor="w")
        ctk.CTkLabel(info, text=f"@{hoi_vien.ten_dang_nhap or 'chưa cấp'}",
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=TEXT_MUTED, anchor="w").pack(anchor="w")

        mau_trang_thai = EMERALD if hoi_vien.trang_thai == "ACTIVE" else RED
        ctk.CTkLabel(tren, text="●",
                     font=ctk.CTkFont(size=14),
                     text_color=mau_trang_thai).pack(side="right", padx=(0, 0))

        # Details
        chi_tiet = ctk.CTkFrame(card, fg_color="#f8fafc", corner_radius=12,
                                border_width=1, border_color=BORDER)
        chi_tiet.pack(fill="x", padx=16, pady=12)

        _TT_VI = {"ACTIVE": "Hoạt động", "EXPIRED": "Hết hạn", "PENDING": "Chờ duyệt"}
        du_lieu_dong = [
            ("📱 Liên hệ", hoi_vien.so_dien_thoai),
            ("📍 Quê quán", hoi_vien.que_quan or "---"),
            ("⚖ Cân nặng", f"{hoi_vien.can_nang or '--'} kg"),
            ("📋 Trạng thái", _TT_VI.get(hoi_vien.trang_thai, hoi_vien.trang_thai)),
        ]
        chi_tiet.grid_columnconfigure(1, weight=1)
        for r, (nhan, gia_tri) in enumerate(du_lieu_dong):
            ctk.CTkLabel(chi_tiet, text=nhan,
                         font=ctk.CTkFont(size=9, weight="bold"),
                         text_color=TEXT_MUTED).grid(row=r, column=0, padx=12, pady=3, sticky="w")
            mau_chu = (EMERALD if hoi_vien.trang_thai == "ACTIVE" else RED) if nhan.endswith("Trạng thái") else TEXT_PRIMARY
            ctk.CTkLabel(chi_tiet, text=gia_tri,
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=mau_chu).grid(row=r, column=1, padx=12, pady=3, sticky="e")

        # Buttons
        hang_nut = ctk.CTkFrame(card, fg_color=WHITE, corner_radius=0)
        hang_nut.pack(fill="x", padx=16, pady=(0, 16))
        hang_nut.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(hang_nut, text="✏ Sửa",
                      fg_color="#f1f5f9", text_color=TEXT_SECONDARY,
                      hover_color="#dbeafe", font=ctk.CTkFont(size=11, weight="bold"),
                      corner_radius=10, height=36,
                      command=lambda m=hoi_vien: self._mo_hop_thoai_sua(m)).grid(row=0, column=0, sticky="ew", padx=(0, 4))

        vai_tro = self.app.nguoi_dung_hien_tai.vai_tro
        if vai_tro not in ("PT",):
            ctk.CTkButton(hang_nut, text="🗑 Xóa",
                          fg_color="#f1f5f9", text_color=TEXT_SECONDARY,
                          hover_color="#fee2e2", font=ctk.CTkFont(size=11, weight="bold"),
                          corner_radius=10, height=36,
                          command=lambda m=hoi_vien: self._xac_nhan_xoa(m)).grid(row=0, column=1, sticky="ew", padx=(4, 0))
        return card

    # ------------------------------------------------------------------
    # Dialogs
    # ------------------------------------------------------------------
    def _mo_hop_thoai_them(self):
        HopThoaiHoiVien(self, tieu_de="Đăng ký Hội Viên Mới",
                         khi_luu=self._luu_them)

    def _mo_hop_thoai_sua(self, hoi_vien):
        HopThoaiHoiVien(self, tieu_de="Cập nhật tài khoản Hội viên",
                         hoi_vien=hoi_vien, khi_luu=self._luu_sua)

    def _luu_them(self, du_lieu: dict):
        try:
            can_nang = float(str(du_lieu["can_nang"]).replace(",", ".")) if str(du_lieu["can_nang"]).strip() else 0.0
        except ValueError:
            can_nang = 0.0

        from utils.validators import bam_mat_khau
        moi = HoiVien(
            id=f"m{int(time.time()*1000)}",
            ho_ten=du_lieu["ho_ten"],
            so_dien_thoai=du_lieu["so_dien_thoai"],
            email=du_lieu["email"],
            que_quan=du_lieu["que_quan"],
            ten_dang_nhap=du_lieu["ten_dang_nhap"],
            mat_khau=bam_mat_khau(du_lieu["mat_khau"]) if du_lieu["mat_khau"] else "",
            ngay_gia_nhap=str(__import__('datetime').date.today()),
            trang_thai="ACTIVE",
            can_nang=can_nang,
            can_nang_truoc_do=0.0
        )
        def _worker():
            try:
                ms.them(moi)
            except Exception as e:
                self.after(0, lambda err=e: self.app.hien_thong_bao(f"Lỗi: {err}", "error"))
            else:
                def _ui():
                    self.app.du_lieu["members"].append(moi)
                    self._lam_moi_danh_sach()
                    self.app.hien_thong_bao(f"Đã thêm hội viên {moi.ho_ten}", "success")
                self.after(0, _ui)
        threading.Thread(target=_worker, daemon=True).start()

    def _luu_sua(self, du_lieu: dict):
        hoi_vien = du_lieu["__hoi_vien__"]
        hoi_vien.ho_ten = du_lieu["ho_ten"]
        hoi_vien.so_dien_thoai = du_lieu["so_dien_thoai"]
        hoi_vien.email    = du_lieu["email"]
        hoi_vien.que_quan = du_lieu["que_quan"]
        hoi_vien.ten_dang_nhap = du_lieu["ten_dang_nhap"]
        if du_lieu["mat_khau"]:
            hoi_vien.mat_khau = du_lieu["mat_khau"]
        try:
            w = float(du_lieu["can_nang"] or hoi_vien.can_nang)
        except ValueError:
            w = hoi_vien.can_nang
        hoi_vien.can_nang = w
        def _worker():
            try:
                ms.cap_nhat(hoi_vien)
            except Exception as e:
                self.after(0, lambda err=e: self.app.hien_thong_bao(f"Lỗi: {err}", "error"))
            else:
                self.after(0, lambda: [
                    self._lam_moi_danh_sach(),
                    self.app.hien_thong_bao(f"Đã cập nhật {hoi_vien.ho_ten}", "success")
                ])
        threading.Thread(target=_worker, daemon=True).start()

    def _xac_nhan_xoa(self, hoi_vien):
        dlg = ctk.CTkToplevel(self)
        dlg.title("Xác nhận xóa")
        w, h = 340, 200
        dlg.geometry(f"{w}x{h}")
        dlg.update_idletasks()
        x = (dlg.winfo_screenwidth() - w) // 2

        y = (dlg.winfo_screenheight() - h) // 2

        dlg.geometry(f"+{x}+{y}")
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.configure(fg_color=WHITE)
        ctk.CTkLabel(dlg, text="🗑 Xóa Hội Viên?",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(pady=(28, 4))
        ctk.CTkLabel(dlg, text=f"Dữ liệu của {hoi_vien.ho_ten}\nsẽ bị xóa vĩnh viễn.",
                     font=ctk.CTkFont(size=11), text_color=TEXT_SECONDARY,
                     justify="center").pack(pady=(0, 20))
        hang = ctk.CTkFrame(dlg, fg_color=WHITE, corner_radius=0)
        hang.pack(fill="x", padx=24)
        ctk.CTkButton(hang, text="Hủy", fg_color="#f1f5f9",
                       text_color=TEXT_SECONDARY, hover_color=BORDER,
                       font=ctk.CTkFont(weight="bold"),
                       command=dlg.destroy).pack(side="left", expand=True, fill="x", padx=(0, 6))
        ctk.CTkButton(hang, text="Xác nhận xóa", fg_color=RED,
                       hover_color="#dc2626", text_color=WHITE,
                       font=ctk.CTkFont(weight="bold"),
                       command=lambda: self._thuc_hien_xoa(hoi_vien, dlg)).pack(side="left", expand=True, fill="x", padx=(6, 0))

    def _thuc_hien_xoa(self, hoi_vien, dlg):
        dlg.destroy()
        def _worker():
            try:
                ms.xoa(hoi_vien.id)
            except Exception as e:
                self.after(0, lambda err=e: self.app.hien_thong_bao(f"Lỗi: {err}", "error"))
            else:
                def _ui():
                    self.app.du_lieu["members"] = [m for m in self.app.du_lieu["members"] if m.id != hoi_vien.id]
                    self._lam_moi_danh_sach()
                    self.app.hien_thong_bao("Đã xóa hội viên thành công", "success")
                self.after(0, _ui)
        threading.Thread(target=_worker, daemon=True).start()


class HopThoaiHoiVien(ctk.CTkToplevel):
    def __init__(self, master, tieu_de, khi_luu, hoi_vien: HoiVien = None):
        super().__init__(master)
        self.title(tieu_de)
        w, h = 620, 640
        self.geometry(f"{w}x{h}")
        self.resizable(False, True)
        self.grab_set()
        self.configure(fg_color=WHITE)
        self.hoi_vien = hoi_vien
        self.khi_luu = khi_luu

        def _can_giua():


            x = (self.winfo_screenwidth() - w) // 2


            y = (self.winfo_screenheight() - h) // 2


            self.geometry(f"+{x}+{y}")
        self.after(10, _can_giua)

        self._tao_giao_dien(tieu_de)

    def _tao_giao_dien(self, tieu_de):
        # Footer (Được ghim dưới cùng để không bị mất khi thu nhỏ)
        chan_trang = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=0, height=72)
        chan_trang.pack(side="bottom", fill="x")
        chan_trang.pack_propagate(False)
        sep2 = ctk.CTkFrame(self, fg_color=BORDER, height=1, corner_radius=0)
        sep2.pack(side="bottom", fill="x")
        
        chan_trang.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(chan_trang, text="Hủy", fg_color="#f1f5f9",
                       text_color=TEXT_SECONDARY, hover_color=BORDER,
                       font=ctk.CTkFont(weight="bold"), height=44, corner_radius=12,
                       command=self.destroy).grid(row=0, column=0, padx=(24, 6), pady=14, sticky="ew")
        text_nut = "Cập nhật thông tin" if self.hoi_vien else "Kích hoạt hội viên"
        mau_nut = BLUE if self.hoi_vien else ORANGE
        ctk.CTkButton(chan_trang, text=text_nut, fg_color=mau_nut,
                       hover_color=ORANGE_DARK if not self.hoi_vien else "#2563eb",
                       text_color=WHITE,
                       font=ctk.CTkFont(weight="bold"), height=44, corner_radius=12,
                       command=self._gui).grid(row=0, column=1, padx=(6, 24), pady=14, sticky="ew")

        # Scrollable body (Chiếm phần diện tích còn lại ở giữa)
        than = ctk.CTkScrollableFrame(self, fg_color=WHITE, corner_radius=0,
                                       scrollbar_button_color=BORDER)
        than.pack(side="top", fill="both", expand=True)

        m = self.hoi_vien

        def tao_o_nhap(cha, nhan, ten_bien, mac_dinh="", hien=""):
            ctk.CTkLabel(cha, text=nhan,
                         font=ctk.CTkFont(size=9, weight="bold"),
                         text_color=TEXT_MUTED, anchor="w").pack(fill="x", pady=(8, 2))
            o = ctk.CTkEntry(cha, height=44, corner_radius=10,
                                  border_color=BORDER, border_width=1,
                                  fg_color="#f8fafc", text_color=TEXT_PRIMARY,
                                  font=ctk.CTkFont(size=13, weight="bold"),
                                  show=hien)
            o.pack(fill="x")
            if mac_dinh:
                o.insert(0, str(mac_dinh))
            setattr(self, f"_{ten_bien}_entry", o)
            return o

        hang1 = ctk.CTkFrame(than, fg_color="transparent")
        hang1.pack(fill="x", padx=12, pady=4)
        hang1.grid_columnconfigure((0, 1), weight=1)

        cot1 = ctk.CTkFrame(hang1, fg_color="transparent")
        cot1.grid(row=0, column=0, sticky="ew", padx=12)
        tao_o_nhap(cot1, "HỌ VÀ TÊN *", "ho_ten", m.ho_ten if m else "")

        cot2 = ctk.CTkFrame(hang1, fg_color="transparent")
        cot2.grid(row=0, column=1, sticky="ew", padx=12)
        tao_o_nhap(cot2, "SỐ ĐIỆN THOẠI *", "so_dien_thoai", m.so_dien_thoai if m else "")

        hang2 = ctk.CTkFrame(than, fg_color="transparent")
        hang2.pack(fill="x", padx=12, pady=4)
        hang2.grid_columnconfigure((0, 1), weight=1)

        cot3 = ctk.CTkFrame(hang2, fg_color="transparent")
        cot3.grid(row=0, column=0, sticky="ew", padx=12)
        tao_o_nhap(cot3, "QUÊ QUÁN", "que_quan", m.que_quan or "" if m else "")

        cot4 = ctk.CTkFrame(hang2, fg_color="transparent")
        cot4.grid(row=0, column=1, sticky="ew", padx=12)
        tao_o_nhap(cot4, "EMAIL *", "email", m.email if m else "")

        # Login section
        khung_dang_nhap = ctk.CTkFrame(than, fg_color="#fff7ed", corner_radius=14,
                                  border_width=1, border_color="#fed7aa")
        khung_dang_nhap.pack(fill="x", padx=24, pady=(16, 0))
        ctk.CTkLabel(khung_dang_nhap, text="THÔNG TIN ĐĂNG NHẬP ỨNG DỤNG",
                     font=ctk.CTkFont(size=9, weight="bold"),
                     text_color=ORANGE).pack(pady=(12, 4))

        hang_2 = ctk.CTkFrame(khung_dang_nhap, fg_color="transparent", corner_radius=0)
        hang_2.pack(fill="x", padx=12, pady=(0, 12))
        hang_2.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(hang_2, text="TÊN ĐĂNG NHẬP *",
                     font=ctk.CTkFont(size=9, weight="bold"),
                     text_color=TEXT_MUTED).grid(row=0, column=0, sticky="w", pady=(0, 2))
        self._ten_dang_nhap_entry = ctk.CTkEntry(hang_2, height=40, corner_radius=8,
                                             border_color=BORDER, border_width=1,
                                             fg_color=WHITE, text_color=TEXT_PRIMARY,
                                             font=ctk.CTkFont(size=12, weight="bold"))
        self._ten_dang_nhap_entry.grid(row=1, column=0, sticky="ew", padx=(0, 6))
        if m and m.ten_dang_nhap:
            self._ten_dang_nhap_entry.insert(0, m.ten_dang_nhap)

        ctk.CTkLabel(hang_2, text="MẬT KHẨU" + (" MỚI" if m else " *"),
                     font=ctk.CTkFont(size=9, weight="bold"),
                     text_color=TEXT_MUTED).grid(row=0, column=1, sticky="w", pady=(0, 2))
        self._mat_khau_entry = ctk.CTkEntry(hang_2, show="●", height=40, corner_radius=8,
                                             border_color=BORDER, border_width=1,
                                             fg_color=WHITE, text_color=TEXT_PRIMARY,
                                             font=ctk.CTkFont(size=12, weight="bold"),
                                             placeholder_text="••••••••")
        self._mat_khau_entry.grid(row=1, column=1, sticky="ew", padx=(6, 0))

        ctk.CTkLabel(hang_2, text="CÂN NẶNG (kg)",
                     font=ctk.CTkFont(size=9, weight="bold"),
                     text_color=TEXT_MUTED).grid(row=2, column=0, sticky="w", pady=(12, 2))
        self._can_nang_entry = ctk.CTkEntry(hang_2, height=40, corner_radius=8,
                                           border_color=BORDER, border_width=1,
                                           fg_color=WHITE, text_color=TEXT_PRIMARY,
                                           font=ctk.CTkFont(size=12, weight="bold"))
        self._can_nang_entry.grid(row=3, column=0, sticky="ew", padx=(0, 6))
        if m and m.can_nang:
            self._can_nang_entry.insert(0, str(m.can_nang))



    def _gui(self):
        from utils.validators import (khong_de_trong, la_so_dien_thoai, la_email,
                                      khong_co_khoang_trang, do_dai_toi_thieu,
                                      la_so_khong_am, kiem_tra_tat_ca)
        ho_ten      = self._ho_ten_entry.get().strip()
        sdt         = self._so_dien_thoai_entry.get().strip()
        email       = self._email_entry.get().strip()
        ten_dn      = self._ten_dang_nhap_entry.get().strip()
        mat_khau    = self._mat_khau_entry.get().strip()
        can_nang    = self._can_nang_entry.get().strip()

        loi_list = kiem_tra_tat_ca([
            khong_de_trong(ho_ten,   "Họ và tên"),
            la_so_dien_thoai(sdt),
            la_email(email),
            khong_de_trong(ten_dn,   "Tên đăng nhập"),
            khong_co_khoang_trang(ten_dn, "Tên đăng nhập"),
            # Mật khẩu bắt buộc khi thêm mới
            (None if self.hoi_vien else khong_de_trong(mat_khau, "Mật khẩu")),
            (None if not mat_khau else do_dai_toi_thieu(mat_khau, 6, "Mật khẩu")),
            la_so_khong_am(can_nang, "Cân nặng"),
        ])

        if loi_list:
            # Tìm app để hiển thị toast
            try:
                frame = self.master
                while frame and not hasattr(frame, 'app'):
                    frame = frame.master
                app = frame.app if frame else None
                if app:
                    app.hien_thong_bao("⚠ " + loi_list[0], "error")
            except Exception:
                pass
            return

        du_lieu = {
            "ho_ten": ho_ten,
            "so_dien_thoai": sdt,
            "email": email,
            "que_quan": self._que_quan_entry.get().strip(),
            "ten_dang_nhap": ten_dn,
            "mat_khau": mat_khau,
            "can_nang": can_nang,
        }
        if self.hoi_vien:
            du_lieu["__hoi_vien__"] = self.hoi_vien
        self.destroy()
        self.khi_luu(du_lieu)

