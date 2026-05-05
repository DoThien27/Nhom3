"""
Huấn luyện viên — Trainers Page
"""
import threading
import customtkinter as ctk
from ui.app import (ORANGE, ORANGE_DARK, ORANGE_LIGHT, WHITE, BG,
                     TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, BORDER, EMERALD, RED, BLUE)
import services.user_service as us
from models.models import NguoiDung
import time


class TrangHuanLuyenVien(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, fg_color=BG, corner_radius=0, **kwargs)
        self.app = app
        self.bien_tim_kiem = ctk.StringVar()
        self.bien_tim_kiem.trace("w", lambda *a: self.app.debounce("trainer_search", self._lam_moi))
        self._tao_giao_dien()

    def _tao_giao_dien(self):
        top = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        top.pack(fill="x", padx=24, pady=(20, 0))

        ctk.CTkLabel(top, text="HUẤN LUYỆN VIÊN",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(side="left")

        ctk.CTkButton(top, text="＋  Thêm HLV mới",
                      font=ctk.CTkFont(size=11, weight="bold"),
                      fg_color=ORANGE, hover_color=ORANGE_DARK,
                      height=40, corner_radius=12,
                      command=self._mo_hop_thoai_them).pack(side="left", padx=16)

        sf = ctk.CTkFrame(top, fg_color=WHITE, corner_radius=12,
                           border_width=1, border_color=BORDER)
        sf.pack(side="right")
        ctk.CTkLabel(sf, text="🔍").pack(side="left", padx=(12, 0))
        ctk.CTkEntry(sf, textvariable=self.bien_tim_kiem,
                     placeholder_text="Tìm HLV...",
                     width=200, height=38, border_width=0,
                     fg_color=WHITE, text_color=TEXT_PRIMARY,
                     font=ctk.CTkFont(size=12)).pack(side="left", padx=8)

        self.vung_cuon = ctk.CTkScrollableFrame(self, fg_color=BG, corner_radius=0,
                                               scrollbar_button_color=BORDER)
        self.vung_cuon.pack(fill="both", expand=True, padx=16, pady=16)
        self._lam_moi()

    def _lam_moi(self):
        for w in self.vung_cuon.winfo_children():
            w.destroy()

        tu_khoa = self.bien_tim_kiem.get().lower()
        danh_sach_hlv = [u for u in self.app.du_lieu["users"]
                    if u.vai_tro == "PT"
                    and (not tu_khoa or tu_khoa in u.ho_ten.lower())]

        if not danh_sach_hlv:
            ctk.CTkLabel(self.vung_cuon, text="Không có huấn luyện viên nào",
                         font=ctk.CTkFont(size=13), text_color=TEXT_MUTED).pack(pady=60)
            return

        COLS = 3
        for col in range(COLS):
            self.vung_cuon.grid_columnconfigure(col, weight=1)
        for i, hlv in enumerate(danh_sach_hlv):
            row = i // COLS
            col = i % COLS

            # Count members assigned
            so_luong_hv = sum(1 for m in self.app.du_lieu["members"]
                          if m.id_pt_phu_trach == hlv.id)

            the = ctk.CTkFrame(self.vung_cuon, fg_color=WHITE, corner_radius=20,
                                 border_width=1, border_color=BORDER)
            the.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

            # Avatar
            chu_cai_dau = (hlv.ho_ten.split()[-1][0] if hlv.ho_ten.strip() else "?").upper()
            ctk.CTkLabel(the, text=chu_cai_dau,
                         font=ctk.CTkFont(size=28, weight="bold"),
                         fg_color="#dbeafe", text_color=BLUE,
                         corner_radius=14, width=64, height=64).pack(pady=(20, 0))

            ctk.CTkLabel(the, text=hlv.ho_ten.upper(),
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=TEXT_PRIMARY).pack(pady=(8, 0))
            ctk.CTkLabel(the, text=f"@{hlv.ten_dang_nhap}",
                         font=ctk.CTkFont(size=10, weight="bold"),
                         text_color=TEXT_MUTED).pack()

            sep = ctk.CTkFrame(the, fg_color=BORDER, height=1, corner_radius=0)
            sep.pack(fill="x", padx=20, pady=12)

            chi_tiet = ctk.CTkFrame(the, fg_color="#f8fafc", corner_radius=12,
                                   border_width=1, border_color=BORDER)
            chi_tiet.pack(fill="x", padx=16, pady=(0, 16))

            du_lieu_dong = [
                ("🎯 Chuyên môn", hlv.chuyen_mon or "Fitness tổng hợp"),
                ("👥 Học viên", f"{so_luong_hv} người"),
            ]
            chi_tiet.grid_columnconfigure(1, weight=1)
            for ri, (nhan, gia_tri) in enumerate(du_lieu_dong):
                ctk.CTkLabel(chi_tiet, text=nhan,
                             font=ctk.CTkFont(size=9, weight="bold"),
                             text_color=TEXT_MUTED).grid(row=ri, column=0, padx=12, pady=6, sticky="w")
                ctk.CTkLabel(chi_tiet, text=gia_tri,
                             font=ctk.CTkFont(size=11, weight="bold"),
                             text_color=TEXT_PRIMARY).grid(row=ri, column=1, padx=12, pady=6, sticky="e")

            vai_tro_ht = self.app.nguoi_dung_hien_tai.vai_tro
            if vai_tro_ht in ("ADMIN", "MANAGER"):
                hang_nut = ctk.CTkFrame(the, fg_color=WHITE, corner_radius=0)
                hang_nut.pack(fill="x", padx=16, pady=(0, 16))
                hang_nut.grid_columnconfigure((0, 1), weight=1)
                
                ctk.CTkButton(hang_nut, text="Sửa", fg_color="#f1f5f9", text_color=TEXT_SECONDARY,
                              hover_color="#dbeafe", corner_radius=10, height=34,
                              font=ctk.CTkFont(size=11, weight="bold"),
                              command=lambda u=hlv: self._mo_hop_thoai_sua(u)).grid(
                    row=0, column=0, sticky="ew", padx=(0, 4))
                
                ctk.CTkButton(hang_nut, text="Xóa", fg_color="#f1f5f9", text_color=TEXT_SECONDARY,
                              hover_color="#fee2e2", corner_radius=10, height=34,
                              font=ctk.CTkFont(size=11, weight="bold"),
                              command=lambda u=hlv: self._xac_nhan_xoa(u)).grid(
                    row=0, column=1, sticky="ew", padx=(4, 0))

    def _mo_hop_thoai_them(self):
        from ui.user_management_page import HopThoaiNhanSu
        HopThoaiNhanSu(self, khi_luu=self._luu_them)

    def _mo_hop_thoai_sua(self, user):
        from ui.user_management_page import HopThoaiNhanSu
        HopThoaiNhanSu(self, user=user, khi_luu=self._luu_sua)

    def _luu_them(self, du_lieu):
        from utils.validators import bam_mat_khau
        user = NguoiDung(
            id=str(int(time.time() * 1000)),
            ho_ten=du_lieu["ho_ten"], ten_dang_nhap=du_lieu["ten_dang_nhap"],
            mat_khau=bam_mat_khau(du_lieu["mat_khau"]),
            vai_tro=du_lieu["vai_tro"],
            chuyen_mon=du_lieu.get("chuyen_mon", "")
        )
        def _worker():
            try:
                us.them(user)
            except Exception as e:
                self.after(0, lambda err=e: self.app.hien_thong_bao(f"Lỗi: {err}", "error"))
            else:
                def _ui():
                    self.app.du_lieu["users"].append(user)
                    self._lam_moi()
                    self.app.hien_thong_bao(f"Đã thêm HLV: {user.ho_ten}", "success")
                self.after(0, _ui)
        threading.Thread(target=_worker, daemon=True).start()

    def _luu_sua(self, du_lieu):
        user = du_lieu["__nguoi_dung__"]
        user.ho_ten = du_lieu["ho_ten"]
        user.ten_dang_nhap = du_lieu["ten_dang_nhap"]
        user.vai_tro = du_lieu["vai_tro"]
        user.chuyen_mon = du_lieu.get("chuyen_mon", "")
        mk_moi = du_lieu.get("mat_khau")
        if mk_moi:
            from utils.validators import bam_mat_khau
            user.mat_khau = bam_mat_khau(mk_moi)
        def _worker():
            try:
                us.cap_nhat(user)
            except Exception as e:
                self.after(0, lambda err=e: self.app.hien_thong_bao(f"Lỗi: {err}", "error"))
            else:
                self.after(0, lambda: [
                    self._lam_moi(),
                    self.app.hien_thong_bao("Đã cập nhật HLV", "success")
                ])
        threading.Thread(target=_worker, daemon=True).start()

    def _xac_nhan_xoa(self, user):
        dlg = ctk.CTkToplevel(self)
        dlg.title("Xác nhận xóa")
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

        ctk.CTkLabel(dlg, text="🗑  Xóa HLV?",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(pady=(28, 4))
        ctk.CTkLabel(dlg, text=f"Tài khoản '{user.ho_ten}'\nsẽ bị xóa vĩnh viễn.",
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
                    self._lam_moi()
                    self.app.hien_thong_bao("Đã xóa HLV thành công", "success")
                self.after(0, _ui)
        threading.Thread(target=_worker, daemon=True).start()
