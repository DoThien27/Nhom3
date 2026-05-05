"""
Quan ly Tai khoan He thong — User Management Page (ADMIN only)
"""
import math
import threading
import customtkinter as ctk
import time
from models.models import NguoiDung
import services.user_service as us
from ui.app import (ORANGE, ORANGE_DARK, ORANGE_LIGHT, WHITE, BG,
                     TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, BORDER, EMERALD, RED, BLUE)

ROLES = ["ADMIN", "MANAGER", "RECEPTIONIST", "PT"]
ROLE_LABELS = {
    "ADMIN": "Quản trị viên",
    "MANAGER": "Quản lý",
    "RECEPTIONIST": "Lễ tân",
    "PT": "Huấn luyện viên",
    "MEMBER": "Hội viên",
}
ROLE_COLORS = {
    "ADMIN": "#7c3aed",
    "MANAGER": BLUE,
    "RECEPTIONIST": EMERALD,
    "PT": ORANGE,
    "MEMBER": "#64748b",
}


class TrangQuanLyNhanSu(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, fg_color=BG, corner_radius=0, **kwargs)
        self.app = app
        self.trang_hien_tai = 1
        self.so_luong_moi_trang = 20
        self._tao_giao_dien()

    def _tao_giao_dien(self):
        top = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        top.pack(fill="x", padx=24, pady=(20, 0))

        ctk.CTkLabel(top, text="QUẢN LÝ HỆ THỐNG",
                     font=ctk.CTkFont(family="Inter", size=20, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(side="left")

        ctk.CTkButton(top, text="＋  Thêm nhân sự",
                       font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                       fg_color=ORANGE, hover_color=ORANGE_DARK,
                       height=44, corner_radius=14,
                       command=self._mo_hop_thoai_them).pack(side="right")

        # Table
        the_bang = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=24,
                                   border_width=1, border_color=BORDER)
        the_bang.pack(fill="both", expand=True, padx=24, pady=16)
        the_bang.grid_rowconfigure(1, weight=1)
        the_bang.grid_columnconfigure(0, weight=1)

        cols = ["Họ tên", "Tên đăng nhập", "Vai trò", "Chuyên môn", ""]
        widths = [220, 160, 140, 220, 160]
        hdr = ctk.CTkFrame(the_bang, fg_color="#f1f5f9", corner_radius=0)
        hdr.grid(row=0, column=0, sticky="ew")
        for ci, (col, w) in enumerate(zip(cols, widths)):
            ctk.CTkLabel(hdr, text=col.upper(),
                         font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                         text_color=TEXT_MUTED, width=w, anchor="center").grid(
                row=0, column=ci, padx=6, pady=12, sticky="ew")

        self.vung_cuon = ctk.CTkScrollableFrame(the_bang, fg_color=WHITE,
                                               corner_radius=0, scrollbar_button_color=BORDER)
        self.vung_cuon.grid(row=1, column=0, sticky="nsew")
        
        # Pagination Bar
        self.khung_phan_trang = ctk.CTkFrame(the_bang, fg_color=WHITE, corner_radius=0)
        self.khung_phan_trang.grid(row=2, column=0, sticky="ew", padx=16, pady=16)
        
        self.nut_trang_truoc = ctk.CTkButton(self.khung_phan_trang, text="< Trang trước", width=120, height=36,
                                             fg_color=WHITE, text_color=TEXT_PRIMARY, border_width=1, border_color=BORDER, hover_color="#f1f5f9",
                                             command=self._trang_truoc)
        self.nut_trang_truoc.pack(side="left")
        
        self.nhan_trang = ctk.CTkLabel(self.khung_phan_trang, text="Trang 1 / 1", font=ctk.CTkFont(family="Inter", size=13, weight="bold"), text_color=TEXT_MUTED)
        self.nhan_trang.pack(side="left", expand=True)
        
        self.nut_trang_sau = ctk.CTkButton(self.khung_phan_trang, text="Trang sau >", width=120, height=36,
                                             fg_color=WHITE, text_color=TEXT_PRIMARY, border_width=1, border_color=BORDER, hover_color="#f1f5f9",
                                             command=self._trang_sau)
        self.nut_trang_sau.pack(side="right")

        self._lam_moi_bang()

    def _trang_truoc(self):
        if self.trang_hien_tai > 1:
            self.trang_hien_tai -= 1
            self._lam_moi_bang()
            
    def _trang_sau(self):
        self.trang_hien_tai += 1
        self._lam_moi_bang()

    def _lam_moi_bang(self):
        for w in self.vung_cuon.winfo_children():
            w.destroy()

        users_list = self.app.du_lieu["users"]
        tong_so = len(users_list)
        so_trang = math.ceil(tong_so / self.so_luong_moi_trang) if tong_so > 0 else 1
        if self.trang_hien_tai > so_trang:
            self.trang_hien_tai = so_trang
            
        self.nhan_trang.configure(text=f"Trang {self.trang_hien_tai} / {so_trang}")
        self.nut_trang_truoc.configure(state="normal" if self.trang_hien_tai > 1 else "disabled")
        self.nut_trang_sau.configure(state="normal" if self.trang_hien_tai < so_trang else "disabled")

        bat_dau = (self.trang_hien_tai - 1) * self.so_luong_moi_trang
        ket_thuc = bat_dau + self.so_luong_moi_trang
        trang_hien_tai_list = users_list[bat_dau:ket_thuc]

        for user in trang_hien_tai_list:
            mau_vai_tro = ROLE_COLORS.get(user.vai_tro, TEXT_MUTED)
            hang = ctk.CTkFrame(self.vung_cuon, fg_color=WHITE, corner_radius=0)
            hang.pack(fill="x")
            ctk.CTkFrame(self.vung_cuon, fg_color=BORDER, height=1, corner_radius=0).pack(fill="x")

            widths = [200, 150, 130, 200]
            vals = [user.ho_ten, user.ten_dang_nhap, ROLE_LABELS.get(user.vai_tro, user.vai_tro), user.chuyen_mon or "---"]
            txt_colors = [TEXT_PRIMARY, TEXT_SECONDARY, mau_vai_tro, TEXT_SECONDARY]
            for ci, (gia_tri, w, mau) in enumerate(zip(vals, widths, txt_colors)):
                ctk.CTkLabel(hang, text=gia_tri,
                             font=ctk.CTkFont(family="Inter", size=13, weight="bold" if ci == 0 else "normal"),
                             text_color=mau, width=w, anchor="center").grid(
                    row=0, column=ci, padx=6, pady=14, sticky="ew")

            khung_nut = ctk.CTkFrame(hang, fg_color=WHITE, corner_radius=0)
            khung_nut.grid(row=0, column=4, padx=8, sticky="")
            ctk.CTkButton(khung_nut, text="✏",
                          fg_color="#f1f5f9", text_color=TEXT_SECONDARY,
                          hover_color="#dbeafe", width=32, height=32, corner_radius=8,
                          command=lambda u=user: self._mo_hop_thoai_sua(u)).pack(side="left", padx=2)
            if user.id != self.app.nguoi_dung_hien_tai.id:
                ctk.CTkButton(khung_nut, text="🗑",
                              fg_color="#f1f5f9", text_color=TEXT_SECONDARY,
                              hover_color="#fee2e2", width=32, height=32, corner_radius=8,
                              command=lambda u=user: self._xac_nhan_xoa(u)).pack(side="left", padx=2)

    def _mo_hop_thoai_them(self):
        HopThoaiNhanSu(self, khi_luu=self._luu_them)

    def _mo_hop_thoai_sua(self, user):
        HopThoaiNhanSu(self, user=user, khi_luu=self._luu_sua)

    def _luu_them(self, du_lieu):
        from utils.validators import bam_mat_khau
        nguoi_dung_moi = NguoiDung(
            id=str(int(time.time() * 1000)),
            ten_dang_nhap=du_lieu["ten_dang_nhap"],
            mat_khau=bam_mat_khau(du_lieu["mat_khau"]) if du_lieu["mat_khau"] else "",
            ho_ten=du_lieu["ho_ten"],
            vai_tro=du_lieu["vai_tro"],
            chuyen_mon=du_lieu["chuyen_mon"]
        )
        def _worker():
            try:
                us.them(nguoi_dung_moi)
            except Exception as e:
                self.after(0, lambda err=e: self.app.hien_thong_bao(f"Lỗi: {err}", "error"))
            else:
                def _ui():
                    self.app.du_lieu["users"].append(nguoi_dung_moi)
                    self._lam_moi_bang()
                    self.app.hien_thong_bao(f"Đã thêm: {nguoi_dung_moi.ho_ten}", "success")
                self.after(0, _ui)
        threading.Thread(target=_worker, daemon=True).start()

    def _luu_sua(self, du_lieu):
        user = du_lieu["__nguoi_dung__"]
        user.ho_ten = du_lieu["ho_ten"]
        user.ten_dang_nhap = du_lieu["ten_dang_nhap"]
        user.vai_tro = du_lieu["vai_tro"]
        user.chuyen_mon = du_lieu["chuyen_mon"]
        if du_lieu["mat_khau"]:
            from utils.validators import bam_mat_khau
            user.mat_khau = bam_mat_khau(du_lieu["mat_khau"])
        def _worker():
            try:
                us.cap_nhat(user)
            except Exception as e:
                self.after(0, lambda err=e: self.app.hien_thong_bao(f"Lỗi: {err}", "error"))
            else:
                self.after(0, lambda: [
                    self._lam_moi_bang(),
                    self.app.hien_thong_bao(f"Đã cập nhật: {user.ho_ten}", "success")
                ])
        threading.Thread(target=_worker, daemon=True).start()

    def _xac_nhan_xoa(self, user):
        dlg = ctk.CTkToplevel(self)
        dlg.title("Xóa nhân sự")
        w, h = 340, 190
        dlg.geometry(f"{w}x{h}")
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.configure(fg_color=WHITE)

        def _can_giua():


            x = (dlg.winfo_screenwidth() - w) // 2


            y = (dlg.winfo_screenheight() - h) // 2


            dlg.geometry(f"+{x}+{y}")
        dlg.after(10, _can_giua)

        ctk.CTkLabel(dlg, text="🗑  Xóa Nhân Sự?",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(pady=(28, 4))
        ctk.CTkLabel(dlg, text=f"Tài khoản của '{user.ho_ten}'\nsẽ bị xóa vĩnh viễn.",
                     font=ctk.CTkFont(size=11), text_color=TEXT_SECONDARY,
                     justify="center").pack(pady=(0, 20))
        hang = ctk.CTkFrame(dlg, fg_color=WHITE)
        hang.pack(fill="x", padx=24)
        ctk.CTkButton(hang, text="Hủy", fg_color="#f1f5f9", text_color=TEXT_SECONDARY,
                      hover_color=BORDER, font=ctk.CTkFont(weight="bold"),
                      command=dlg.destroy).pack(side="left", expand=True, fill="x", padx=(0, 6))
        ctk.CTkButton(hang, text="Xác nhận xóa", fg_color=RED, hover_color="#dc2626",
                      text_color=WHITE, font=ctk.CTkFont(weight="bold"),
                      command=lambda: self._thuc_hien_xoa(user, dlg)).pack(
            side="left", expand=True, fill="x", padx=(6, 0))

    def _thuc_hien_xoa(self, user, dlg):
        dlg.destroy()
        def _worker():
            try:
                us.xoa(user.id)
            except Exception as e:
                self.after(0, lambda err=e: self.app.hien_thong_bao(f"Lỗi: {err}", "error"))
            else:
                def _ui():
                    self.app.du_lieu["users"] = [u for u in self.app.du_lieu["users"] if u.id != user.id]
                    self._lam_moi_bang()
                    self.app.hien_thong_bao("Đã xóa nhân sự thành công", "success")
                self.after(0, _ui)
        threading.Thread(target=_worker, daemon=True).start()


class HopThoaiNhanSu(ctk.CTkToplevel):
    def __init__(self, master, khi_luu, user: NguoiDung = None):
        super().__init__(master)
        self.title("Cập nhật nhân sự" if user else "Thêm nhân sự mới")
        w, h = 600, 500
        self.geometry(f"{w}x{h}")
        self.resizable(False, False)
        self.grab_set()
        self.configure(fg_color=WHITE)
        self.user = user
        self.khi_luu = khi_luu

        def _can_giua():


            x = (self.winfo_screenwidth() - w) // 2


            y = (self.winfo_screenheight() - h) // 2


            self.geometry(f"+{x}+{y}")
        self.after(10, _can_giua)

        self._tao_giao_dien()

    def _tao_giao_dien(self):
        u = self.user
        tieu_de = "CẬP NHẬT NHÂN SỰ" if u else "THÊM NHÂN SỰ MỚI"



        # Footer (pack trước để giữ chỗ ở dưới)
        chan = ctk.CTkFrame(self, fg_color=WHITE, height=72, corner_radius=0)
        chan.pack(side="bottom", fill="x")
        chan.pack_propagate(False)
        ctk.CTkFrame(self, fg_color=BORDER, height=1, corner_radius=0).pack(side="bottom", fill="x")

        # Body
        than = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=0)
        than.pack(side="top", fill="both", expand=True)

        def tao_o(cha, nhan, mac_dinh="", hien=""):
            ctk.CTkLabel(cha, text=nhan,
                         font=ctk.CTkFont(size=9, weight="bold"),
                         text_color=TEXT_MUTED, anchor="w").pack(fill="x", pady=(8, 2))
            o = ctk.CTkEntry(cha, height=44, corner_radius=10,
                             border_color=BORDER, border_width=1,
                             fg_color="#f8fafc", text_color=TEXT_PRIMARY,
                             font=ctk.CTkFont(size=13, weight="bold"), show=hien)
            o.pack(fill="x")
            if mac_dinh:
                o.insert(0, str(mac_dinh))
            return o

        # Row 1: Họ tên & Tên đăng nhập
        hang1 = ctk.CTkFrame(than, fg_color="transparent")
        hang1.pack(fill="x", padx=16, pady=(12, 0))
        hang1.grid_columnconfigure((0, 1), weight=1)
        c1 = ctk.CTkFrame(hang1, fg_color="transparent")
        c1.grid(row=0, column=0, sticky="ew", padx=(8, 6))
        self._ho_ten = tao_o(c1, "HỌ VÀ TÊN *", u.ho_ten if u else "")
        c2 = ctk.CTkFrame(hang1, fg_color="transparent")
        c2.grid(row=0, column=1, sticky="ew", padx=(6, 8))
        self._ten_dang_nhap = tao_o(c2, "TÊN ĐĂNG NHẬP *", u.ten_dang_nhap if u else "")

        # Row 2: Mật khẩu & Chuyên môn
        hang2 = ctk.CTkFrame(than, fg_color="transparent")
        hang2.pack(fill="x", padx=16)
        hang2.grid_columnconfigure((0, 1), weight=1)
        c3 = ctk.CTkFrame(hang2, fg_color="transparent")
        c3.grid(row=0, column=0, sticky="ew", padx=(8, 6))
        self._mat_khau = tao_o(c3, "MẬT KHẨU" + (" MỚI" if u else " *"), hien="●")
        c4 = ctk.CTkFrame(hang2, fg_color="transparent")
        c4.grid(row=0, column=1, sticky="ew", padx=(6, 8))
        self._chuyen_mon = tao_o(c4, "CHUYÊN MÔN", u.chuyen_mon or "" if u else "")

        # Vai trò
        ctk.CTkLabel(than, text="VAI TRÒ *",
                     font=ctk.CTkFont(size=9, weight="bold"),
                     text_color=TEXT_MUTED, anchor="w").pack(fill="x", padx=24, pady=(12, 2))
        self._bien_vai_tro = ctk.StringVar(value=u.vai_tro if u else "PT")
        khung_vai_tro = ctk.CTkFrame(than, fg_color="#f1f5f9", corner_radius=10)
        khung_vai_tro.pack(fill="x", padx=24)
        for role in ROLES:
            ctk.CTkRadioButton(khung_vai_tro, text=ROLE_LABELS.get(role, role),
                               variable=self._bien_vai_tro, value=role,
                               fg_color=ORANGE,
                               font=ctk.CTkFont(size=11, weight="bold"),
                               text_color=TEXT_PRIMARY).pack(side="left", padx=10, pady=10)

        # Footer buttons
        chan.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(chan, text="Hủy", fg_color="#f1f5f9",
                      text_color=TEXT_SECONDARY, hover_color=BORDER,
                      font=ctk.CTkFont(weight="bold"), height=44, corner_radius=12,
                      command=self.destroy).grid(row=0, column=0, padx=(24, 6), pady=14, sticky="ew")
        ctk.CTkButton(chan, text="💾  Lưu", fg_color=ORANGE, hover_color=ORANGE_DARK,
                      text_color=WHITE, height=44, corner_radius=12,
                      font=ctk.CTkFont(weight="bold"),
                      command=self._gui).grid(row=0, column=1, padx=(6, 24), pady=14, sticky="ew")

    def _gui(self):
        from utils.validators import (khong_de_trong, khong_co_khoang_trang,
                                      do_dai_toi_thieu, kiem_tra_tat_ca)
        ho_ten   = self._ho_ten.get().strip()
        ten_dn   = self._ten_dang_nhap.get().strip()
        mat_khau = self._mat_khau.get().strip()

        loi_list = kiem_tra_tat_ca([
            khong_de_trong(ho_ten,  "Họ và tên"),
            khong_de_trong(ten_dn,  "Tên đăng nhập"),
            khong_co_khoang_trang(ten_dn, "Tên đăng nhập"),
            # Bắt buộc mật khẩu khi thêm mới
            (None if self.user else khong_de_trong(mat_khau, "Mật khẩu")),
            (None if not mat_khau else do_dai_toi_thieu(mat_khau, 6, "Mật khẩu")),
        ])

        if loi_list:
            try:
                frame = self.master
                while frame and not hasattr(frame, 'app'):
                    frame = getattr(frame, 'master', None)
                app = frame.app if frame and hasattr(frame, 'app') else None
                if app:
                    app.hien_thong_bao("⚠ " + loi_list[0], "error")
            except Exception:
                pass
            return

        du_lieu = {
            "ho_ten": ho_ten,
            "ten_dang_nhap": ten_dn,
            "mat_khau": mat_khau,
            "chuyen_mon": self._chuyen_mon.get().strip(),
            "vai_tro": self._bien_vai_tro.get(),
        }
        if self.user:
            du_lieu["__nguoi_dung__"] = self.user
        self.destroy()
        self.khi_luu(du_lieu)

