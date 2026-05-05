"""
Trang Quản Lý Môn Thể Thao — Sports Page
"""
import time
import threading
import customtkinter as ctk
from services.sport_service import MonTheThao
import services.sport_service as sps
from ui.app import (ORANGE, ORANGE_DARK, ORANGE_LIGHT, WHITE, BG,
                    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, BORDER, EMERALD, RED, BLUE)

SPORT_ICONS = {
    "Bóng đá": "⚽", "Cầu lông": "🏸", "Bóng chuyền": "🏐",
    "Bơi lội": "🏊", "Yoga": "🧘", "Gym": "🏋️", "Võ thuật": "🥊",
}


class TrangMonTheThao(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, fg_color=BG, corner_radius=0, **kwargs)
        self.app = app
        self.bien_tim_kiem = ctk.StringVar()
        self.bien_tim_kiem.trace("w", lambda *a: self.app.debounce("sport_search", self._lam_moi))
        self._tao_giao_dien()

    def _tao_giao_dien(self):
        top = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        top.pack(fill="x", padx=24, pady=(20, 0))

        ctk.CTkLabel(top, text="MÔN THỂ THAO",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(side="left")

        vai_tro = self.app.nguoi_dung_hien_tai.vai_tro
        if vai_tro in ("ADMIN", "MANAGER"):
            ctk.CTkButton(top, text="＋  Thêm môn",
                          font=ctk.CTkFont(size=11, weight="bold"),
                          fg_color=ORANGE, hover_color=ORANGE_DARK,
                          height=40, corner_radius=12,
                          command=self._mo_them).pack(side="right")

        sf = ctk.CTkFrame(top, fg_color=WHITE, corner_radius=12,
                          border_width=1, border_color=BORDER)
        sf.pack(side="right", padx=(0, 12))
        ctk.CTkLabel(sf, text="🔍").pack(side="left", padx=(12, 0))
        ctk.CTkEntry(sf, textvariable=self.bien_tim_kiem,
                     placeholder_text="Tìm môn thể thao...",
                     width=200, height=38, border_width=0,
                     fg_color=WHITE, text_color=TEXT_PRIMARY,
                     font=ctk.CTkFont(size=12)).pack(side="left", padx=8)

        self.vung_cuon = ctk.CTkScrollableFrame(self, fg_color=BG, corner_radius=0,
                                                scrollbar_button_color=BORDER)
        self.vung_cuon.pack(fill="both", expand=True, padx=16, pady=16)
        self._lam_moi()

    def _lam_moi_danh_sach(self):
        """Reload sports from DB then refresh UI."""
        def _worker():
            sports = sps.lay_tat_ca()
            self.app.du_lieu["sports"] = sports
            self.after(0, self._lam_moi)
        threading.Thread(target=_worker, daemon=True).start()

    def _lam_moi(self):
        for w in self.vung_cuon.winfo_children():
            w.destroy()
        tu_khoa = self.bien_tim_kiem.get().lower()
        ds = [s for s in self.app.du_lieu.get("sports", [])
              if not tu_khoa or tu_khoa in s.ten.lower()]

        if not ds:
            ctk.CTkLabel(self.vung_cuon, text="Chưa có môn thể thao nào.",
                         font=ctk.CTkFont(size=13), text_color=TEXT_MUTED).pack(pady=60)
            return

        COLS = 4
        for col in range(COLS):
            self.vung_cuon.grid_columnconfigure(col, weight=1)

        vai_tro = self.app.nguoi_dung_hien_tai.vai_tro
        for i, mon in enumerate(ds):
            icon = SPORT_ICONS.get(mon.ten, "🏆")
            row_i = i // COLS
            col_i = i % COLS
            active = mon.trang_thai == "ACTIVE"

            the = ctk.CTkFrame(self.vung_cuon, fg_color=WHITE, corner_radius=20,
                               border_width=1, border_color=BORDER)
            the.grid(row=row_i, column=col_i, padx=8, pady=8, sticky="nsew")

            # Icon + tên
            hdr = ctk.CTkFrame(the, fg_color=ORANGE if active else "#f1f5f9", corner_radius=14)
            hdr.pack(fill="x", padx=12, pady=(12, 0))
            ctk.CTkLabel(hdr, text=icon, font=ctk.CTkFont(size=28)).pack(pady=(12, 0))
            ctk.CTkLabel(hdr, text=mon.ten,
                         font=ctk.CTkFont(size=14, weight="bold"),
                         text_color=WHITE if active else TEXT_MUTED).pack(pady=(4, 10))

            # Mô tả
            ctk.CTkLabel(the, text=mon.mo_ta or "Chưa có mô tả",
                         font=ctk.CTkFont(size=11), text_color=TEXT_SECONDARY,
                         wraplength=160).pack(padx=12, pady=8)

            # Trạng thái badge
            badge_bg = "#dcfce7" if active else "#f1f5f9"
            badge_fg = EMERALD if active else TEXT_MUTED
            badge = ctk.CTkFrame(the, fg_color=badge_bg, corner_radius=8)
            badge.pack(padx=12, pady=(0, 8))
            ctk.CTkLabel(badge, text="● Hoạt động" if active else "○ Vô hiệu",
                         font=ctk.CTkFont(size=10, weight="bold"),
                         text_color=badge_fg).pack(padx=10, pady=4)

            if vai_tro in ("ADMIN", "MANAGER"):
                btn_f = ctk.CTkFrame(the, fg_color=WHITE, corner_radius=0)
                btn_f.pack(fill="x", padx=12, pady=(0, 12))
                btn_f.grid_columnconfigure((0, 1), weight=1)
                ctk.CTkButton(btn_f, text="✏ Sửa",
                              fg_color="#f1f5f9", text_color=TEXT_SECONDARY,
                              hover_color="#dbeafe", corner_radius=10, height=32,
                              font=ctk.CTkFont(size=11, weight="bold"),
                              command=lambda m=mon: self._mo_sua(m)).grid(
                    row=0, column=0, sticky="ew", padx=(0, 3))
                ctk.CTkButton(btn_f, text="🗑 Xóa",
                              fg_color="#f1f5f9", text_color=TEXT_SECONDARY,
                              hover_color="#fee2e2", corner_radius=10, height=32,
                              font=ctk.CTkFont(size=11, weight="bold"),
                              command=lambda m=mon: self._xac_nhan_xoa(m)).grid(
                    row=0, column=1, sticky="ew", padx=(3, 0))

    def _mo_them(self):
        _HopThoaiSport(self, app=self.app, khi_luu=self._luu_them)

    def _mo_sua(self, mon):
        _HopThoaiSport(self, app=self.app, mon=mon, khi_luu=self._luu_sua)

    def _luu_them(self, data):
        mon = MonTheThao(
            id=str(int(time.time() * 1000)),
            ten=data["ten"], mo_ta=data["mo_ta"], trang_thai=data["trang_thai"]
        )
        def _w():
            try:
                sps.them(mon)
            except Exception as e:
                self.after(0, lambda: self.app.hien_thong_bao(f"Lỗi: {e}", "error"))
            else:
                def _ui():
                    self.app.du_lieu["sports"].append(mon)
                    self._lam_moi()
                    self.app.hien_thong_bao(f"Đã thêm môn: {mon.ten}", "success")
                self.after(0, _ui)
        threading.Thread(target=_w, daemon=True).start()

    def _luu_sua(self, data):
        mon = data["__mon__"]
        mon.ten = data["ten"]
        mon.mo_ta = data["mo_ta"]
        mon.trang_thai = data["trang_thai"]
        def _w():
            try:
                sps.cap_nhat(mon)
            except Exception as e:
                self.after(0, lambda: self.app.hien_thong_bao(f"Lỗi: {e}", "error"))
            else:
                self.after(0, lambda: [self._lam_moi(), self.app.hien_thong_bao("Đã cập nhật môn thể thao", "success")])
        threading.Thread(target=_w, daemon=True).start()

    def _xac_nhan_xoa(self, mon):
        dlg = ctk.CTkToplevel(self)
        dlg.title("Xóa môn thể thao")
        w, h = 340, 180
        dlg.geometry(f"{w}x{h}")
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.configure(fg_color=WHITE)
        dlg.after(10, lambda: dlg.geometry(f"+{(dlg.winfo_screenwidth()-w)//2}+{(dlg.winfo_screenheight()-h)//2}"))
        ctk.CTkLabel(dlg, text=f"🗑  Xóa môn '{mon.ten}'?",
                     font=ctk.CTkFont(size=14, weight="bold"), text_color=TEXT_PRIMARY).pack(pady=(24, 8))
        ctk.CTkLabel(dlg, text="Hành động này không thể hoàn tác.",
                     font=ctk.CTkFont(size=11), text_color=TEXT_SECONDARY).pack()
        f = ctk.CTkFrame(dlg, fg_color=WHITE)
        f.pack(fill="x", padx=24, pady=16)
        ctk.CTkButton(f, text="Hủy", fg_color="#f1f5f9", text_color=TEXT_SECONDARY,
                      hover_color=BORDER, font=ctk.CTkFont(weight="bold"),
                      command=dlg.destroy).pack(side="left", expand=True, fill="x", padx=(0, 6))
        ctk.CTkButton(f, text="Xóa", fg_color=RED, hover_color="#dc2626",
                      text_color=WHITE, font=ctk.CTkFont(weight="bold"),
                      command=lambda: self._thuc_hien_xoa(mon, dlg)).pack(side="left", expand=True, fill="x", padx=(6, 0))

    def _thuc_hien_xoa(self, mon, dlg):
        dlg.destroy()
        def _w():
            try:
                sps.xoa(mon.id)
            except Exception as e:
                self.after(0, lambda: self.app.hien_thong_bao(f"Lỗi: {e}", "error"))
            else:
                def _ui():
                    self.app.du_lieu["sports"] = [s for s in self.app.du_lieu["sports"] if s.id != mon.id]
                    self._lam_moi()
                    self.app.hien_thong_bao("Đã xóa môn thể thao", "success")
                self.after(0, _ui)
        threading.Thread(target=_w, daemon=True).start()


class _HopThoaiSport(ctk.CTkToplevel):
    def __init__(self, master, app, khi_luu, mon: MonTheThao = None):
        super().__init__(master)
        self.title("Sửa môn thể thao" if mon else "Thêm môn thể thao")
        w, h = 480, 360
        self.geometry(f"{w}x{h}")
        self.resizable(False, False)
        self.grab_set()
        self.configure(fg_color=WHITE)
        self.app = app
        self.mon = mon
        self.khi_luu = khi_luu
        self.after(10, lambda: self.geometry(f"+{(self.winfo_screenwidth()-w)//2}+{(self.winfo_screenheight()-h)//2}"))
        self._tao_giao_dien()

    def _tao_giao_dien(self):
        m = self.mon
        chan = ctk.CTkFrame(self, fg_color=WHITE, height=72, corner_radius=0)
        chan.pack(side="bottom", fill="x")
        chan.pack_propagate(False)
        ctk.CTkFrame(self, fg_color=BORDER, height=1, corner_radius=0).pack(side="bottom", fill="x")
        than = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=0)
        than.pack(fill="both", expand=True, padx=24, pady=16)

        def field(parent, label, val="", ph=""):
            ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=9, weight="bold"),
                         text_color=TEXT_MUTED, anchor="w").pack(fill="x", pady=(8, 2))
            e = ctk.CTkEntry(parent, height=40, corner_radius=8, border_color=BORDER,
                             fg_color="#f8fafc", text_color=TEXT_PRIMARY,
                             font=ctk.CTkFont(size=13), placeholder_text=ph)
            e.pack(fill="x")
            if val:
                e.insert(0, str(val))
            return e

        self._ten = field(than, "TÊN MÔN THỂ THAO *", m.ten if m else "", "VD: Bóng đá")
        self._mo_ta = field(than, "MÔ TẢ", m.mo_ta if m else "", "Mô tả ngắn gọn...")

        ctk.CTkLabel(than, text="TRẠNG THÁI", font=ctk.CTkFont(size=9, weight="bold"),
                     text_color=TEXT_MUTED, anchor="w").pack(fill="x", pady=(8, 2))
        _TT_HIEN = {"ACTIVE": "Hoạt động", "INACTIVE": "Vô hiệu"}
        _TT_DB   = {v: k for k, v in _TT_HIEN.items()}
        _tt_init = _TT_HIEN.get(m.trang_thai, "Hoạt động") if m else "Hoạt động"
        self._bien_tt_hien = ctk.StringVar(value=_tt_init)
        self._tt_db_map = _TT_DB
        self._combo_tt = ctk.CTkComboBox(than, values=list(_TT_HIEN.values()),
                                         variable=self._bien_tt_hien,
                                         height=40, corner_radius=8, border_color=BORDER,
                                         fg_color="#f8fafc", text_color=TEXT_PRIMARY,
                                         button_color=ORANGE)
        self._combo_tt.pack(fill="x")

        chan.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(chan, text="Hủy", fg_color="#f1f5f9", text_color=TEXT_SECONDARY,
                      hover_color=BORDER, font=ctk.CTkFont(weight="bold"), height=44, corner_radius=12,
                      command=self.destroy).grid(row=0, column=0, padx=(24, 6), pady=14, sticky="ew")
        ctk.CTkButton(chan, text="💾  Lưu", fg_color=ORANGE, hover_color=ORANGE_DARK,
                      text_color=WHITE, height=44, corner_radius=12,
                      font=ctk.CTkFont(weight="bold"),
                      command=self._gui).grid(row=0, column=1, padx=(6, 24), pady=14, sticky="ew")

    def _gui(self):
        ten = self._ten.get().strip()
        if not ten:
            self.app.hien_thong_bao("Tên môn không được để trống", "error")
            return
        data = {"ten": ten, "mo_ta": self._mo_ta.get().strip(), "trang_thai": self._tt_db_map.get(self._bien_tt_hien.get(), self._bien_tt_hien.get())}
        if self.mon:
            data["__mon__"] = self.mon
        self.destroy()
        self.khi_luu(data)
