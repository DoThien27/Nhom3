"""
Trang Quản Lý Sân Bãi / Phòng Tập — Facilities Page
"""
import time
import threading
import customtkinter as ctk
from services.facility_service import SanBai
import services.facility_service as fs
from ui.app import (ORANGE, ORANGE_DARK, ORANGE_LIGHT, WHITE, BG,
                    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, BORDER, EMERALD, RED, BLUE)

LOAI_SAN = ["Sân ngoài trời", "Sân trong nhà", "Phòng trong nhà", "Ngoài trời", "Hồ bơi", "Khác"]


class TrangSanBai(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, fg_color=BG, corner_radius=0, **kwargs)
        self.app = app
        self.bien_tim_kiem = ctk.StringVar()
        self.bien_tim_kiem.trace("w", lambda *a: self.app.debounce("facility_search", self._lam_moi))
        self._tao_giao_dien()

    def _tao_giao_dien(self):
        top = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        top.pack(fill="x", padx=24, pady=(20, 0))
        ctk.CTkLabel(top, text="SÂN BÃI / PHÒNG TẬP",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(side="left")

        vai_tro = self.app.nguoi_dung_hien_tai.vai_tro
        if vai_tro in ("ADMIN", "MANAGER"):
            ctk.CTkButton(top, text="＋  Thêm sân/phòng",
                          font=ctk.CTkFont(size=11, weight="bold"),
                          fg_color=ORANGE, hover_color=ORANGE_DARK,
                          height=40, corner_radius=12,
                          command=self._mo_them).pack(side="right")

        sf = ctk.CTkFrame(top, fg_color=WHITE, corner_radius=12,
                          border_width=1, border_color=BORDER)
        sf.pack(side="right", padx=(0, 12))
        ctk.CTkLabel(sf, text="🔍").pack(side="left", padx=(12, 0))
        ctk.CTkEntry(sf, textvariable=self.bien_tim_kiem,
                     placeholder_text="Tìm sân/phòng...",
                     width=200, height=38, border_width=0,
                     fg_color=WHITE, text_color=TEXT_PRIMARY,
                     font=ctk.CTkFont(size=12)).pack(side="left", padx=8)

        self.vung_cuon = ctk.CTkScrollableFrame(self, fg_color=BG, corner_radius=0,
                                                scrollbar_button_color=BORDER)
        self.vung_cuon.pack(fill="both", expand=True, padx=16, pady=16)
        self._lam_moi()

    def _lam_moi_danh_sach(self):
        def _worker():
            facs = fs.lay_tat_ca()
            self.app.du_lieu["facilities"] = facs
            self.after(0, self._lam_moi)
        threading.Thread(target=_worker, daemon=True).start()

    def _lam_moi(self):
        for w in self.vung_cuon.winfo_children():
            w.destroy()
        tu_khoa = self.bien_tim_kiem.get().lower()
        ds = [f for f in self.app.du_lieu.get("facilities", [])
              if not tu_khoa or tu_khoa in f.ten.lower() or tu_khoa in f.loai.lower()]

        if not ds:
            ctk.CTkLabel(self.vung_cuon, text="Chưa có sân bãi/phòng tập nào.",
                         font=ctk.CTkFont(size=13), text_color=TEXT_MUTED).pack(pady=60)
            return

        COLS = 3
        for col in range(COLS):
            self.vung_cuon.grid_columnconfigure(col, weight=1)

        vai_tro = self.app.nguoi_dung_hien_tai.vai_tro
        for i, san in enumerate(ds):
            active = san.trang_thai == "ACTIVE"
            row_i = i // COLS
            col_i = i % COLS

            the = ctk.CTkFrame(self.vung_cuon, fg_color=WHITE, corner_radius=20,
                               border_width=1, border_color=BORDER)
            the.grid(row=row_i, column=col_i, padx=8, pady=8, sticky="nsew")

            hdr = ctk.CTkFrame(the, fg_color=BLUE if active else "#f1f5f9", corner_radius=14)
            hdr.pack(fill="x", padx=12, pady=(12, 0))
            ctk.CTkLabel(hdr, text="🏟️", font=ctk.CTkFont(size=24)).pack(pady=(10, 0))
            ctk.CTkLabel(hdr, text=san.ten,
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=WHITE if active else TEXT_MUTED).pack(pady=(2, 10))

            chi_tiet = ctk.CTkFrame(the, fg_color="#f8fafc", corner_radius=12, border_width=1, border_color=BORDER)
            chi_tiet.pack(fill="x", padx=12, pady=8)
            chi_tiet.grid_columnconfigure(1, weight=1)
            for ri, (nhan, val) in enumerate([
                ("📂 Loại", san.loai or "—"),
                ("📍 Vị trí", san.vi_tri or "—"),
                ("👥 Sức chứa", f"{san.suc_chua} người"),
                ("📊 Trạng thái", "Hoạt động" if active else "Vô hiệu"),
            ]):
                ctk.CTkLabel(chi_tiet, text=nhan, font=ctk.CTkFont(size=9, weight="bold"),
                             text_color=TEXT_MUTED).grid(row=ri, column=0, padx=12, pady=4, sticky="w")
                ctk.CTkLabel(chi_tiet, text=val, font=ctk.CTkFont(size=11, weight="bold"),
                             text_color=EMERALD if val == "Hoạt động" else TEXT_PRIMARY).grid(
                    row=ri, column=1, padx=12, pady=4, sticky="e")

            if vai_tro in ("ADMIN", "MANAGER"):
                btn_f = ctk.CTkFrame(the, fg_color=WHITE, corner_radius=0)
                btn_f.pack(fill="x", padx=12, pady=(0, 12))
                btn_f.grid_columnconfigure((0, 1), weight=1)
                ctk.CTkButton(btn_f, text="✏ Sửa", fg_color="#f1f5f9", text_color=TEXT_SECONDARY,
                              hover_color="#dbeafe", corner_radius=10, height=32,
                              font=ctk.CTkFont(size=11, weight="bold"),
                              command=lambda s=san: self._mo_sua(s)).grid(row=0, column=0, sticky="ew", padx=(0, 3))
                ctk.CTkButton(btn_f, text="🗑 Xóa", fg_color="#f1f5f9", text_color=TEXT_SECONDARY,
                              hover_color="#fee2e2", corner_radius=10, height=32,
                              font=ctk.CTkFont(size=11, weight="bold"),
                              command=lambda s=san: self._xac_nhan_xoa(s)).grid(row=0, column=1, sticky="ew", padx=(3, 0))

    def _mo_them(self):
        _HopThoaiSan(self, app=self.app, khi_luu=self._luu_them)

    def _mo_sua(self, san):
        _HopThoaiSan(self, app=self.app, san=san, khi_luu=self._luu_sua)

    def _luu_them(self, data):
        san = SanBai(
            id=str(int(time.time() * 1000)),
            ten=data["ten"], loai=data["loai"],
            vi_tri=data["vi_tri"], suc_chua=data["suc_chua"],
            trang_thai=data["trang_thai"]
        )
        def _w():
            try:
                fs.them(san)
            except Exception as e:
                self.after(0, lambda: self.app.hien_thong_bao(f"Lỗi: {e}", "error"))
            else:
                def _ui():
                    self.app.du_lieu["facilities"].append(san)
                    self._lam_moi()
                    self.app.hien_thong_bao(f"Đã thêm: {san.ten}", "success")
                self.after(0, _ui)
        threading.Thread(target=_w, daemon=True).start()

    def _luu_sua(self, data):
        san = data["__san__"]
        san.ten = data["ten"]
        san.loai = data["loai"]
        san.vi_tri = data["vi_tri"]
        san.suc_chua = data["suc_chua"]
        san.trang_thai = data["trang_thai"]
        def _w():
            try:
                fs.cap_nhat(san)
            except Exception as e:
                self.after(0, lambda: self.app.hien_thong_bao(f"Lỗi: {e}", "error"))
            else:
                self.after(0, lambda: [self._lam_moi(), self.app.hien_thong_bao("Đã cập nhật sân/phòng", "success")])
        threading.Thread(target=_w, daemon=True).start()

    def _xac_nhan_xoa(self, san):
        dlg = ctk.CTkToplevel(self)
        dlg.title("Xóa sân bãi/phòng tập")
        w, h = 340, 180
        dlg.geometry(f"{w}x{h}")
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.configure(fg_color=WHITE)
        dlg.after(10, lambda: dlg.geometry(f"+{(dlg.winfo_screenwidth()-w)//2}+{(dlg.winfo_screenheight()-h)//2}"))
        ctk.CTkLabel(dlg, text=f"🗑  Xóa '{san.ten}'?",
                     font=ctk.CTkFont(size=14, weight="bold"), text_color=TEXT_PRIMARY).pack(pady=(24, 8))
        ctk.CTkLabel(dlg, text="Hành động này không thể hoàn tác.",
                     font=ctk.CTkFont(size=11), text_color=TEXT_SECONDARY).pack()
        f = ctk.CTkFrame(dlg, fg_color=WHITE)
        f.pack(fill="x", padx=24, pady=16)
        ctk.CTkButton(f, text="Hủy", fg_color="#f1f5f9", text_color=TEXT_SECONDARY,
                      hover_color=BORDER, command=dlg.destroy).pack(side="left", expand=True, fill="x", padx=(0, 6))
        ctk.CTkButton(f, text="Xóa", fg_color=RED, hover_color="#dc2626", text_color=WHITE,
                      command=lambda: self._thuc_hien_xoa(san, dlg)).pack(side="left", expand=True, fill="x", padx=(6, 0))

    def _thuc_hien_xoa(self, san, dlg):
        dlg.destroy()
        def _w():
            try:
                fs.xoa(san.id)
            except Exception as e:
                self.after(0, lambda: self.app.hien_thong_bao(f"Lỗi: {e}", "error"))
            else:
                def _ui():
                    self.app.du_lieu["facilities"] = [f for f in self.app.du_lieu["facilities"] if f.id != san.id]
                    self._lam_moi()
                    self.app.hien_thong_bao("Đã xóa sân/phòng", "success")
                self.after(0, _ui)
        threading.Thread(target=_w, daemon=True).start()


class _HopThoaiSan(ctk.CTkToplevel):
    def __init__(self, master, app, khi_luu, san: SanBai = None):
        super().__init__(master)
        self.title("Sửa sân/phòng" if san else "Thêm sân/phòng")
        w, h = 500, 420
        self.geometry(f"{w}x{h}")
        self.resizable(False, False)
        self.grab_set()
        self.configure(fg_color=WHITE)
        self.app = app
        self.san = san
        self.khi_luu = khi_luu
        self.after(10, lambda: self.geometry(f"+{(self.winfo_screenwidth()-w)//2}+{(self.winfo_screenheight()-h)//2}"))
        self._tao_giao_dien()

    def _tao_giao_dien(self):
        s = self.san
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

        hang1 = ctk.CTkFrame(than, fg_color="transparent")
        hang1.pack(fill="x")
        hang1.grid_columnconfigure((0, 1), weight=1)
        c1 = ctk.CTkFrame(hang1, fg_color="transparent")
        c1.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self._ten = field(c1, "TÊN SÂN/PHÒNG *", s.ten if s else "", "VD: Sân cầu lông số 1")
        c2 = ctk.CTkFrame(hang1, fg_color="transparent")
        c2.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        self._vi_tri = field(c2, "VỊ TRÍ", s.vi_tri if s else "", "VD: Khu A")

        hang2 = ctk.CTkFrame(than, fg_color="transparent")
        hang2.pack(fill="x")
        hang2.grid_columnconfigure((0, 1), weight=1)
        c3 = ctk.CTkFrame(hang2, fg_color="transparent")
        c3.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self._suc_chua = field(c3, "SỨC CHỨA (người)", str(s.suc_chua) if s else "20", "20")

        # Loại
        ctk.CTkLabel(than, text="LOẠI SÂN/PHÒNG", font=ctk.CTkFont(size=9, weight="bold"),
                     text_color=TEXT_MUTED, anchor="w").pack(fill="x", pady=(8, 2))
        self._combo_loai = ctk.CTkComboBox(than, values=LOAI_SAN, height=40, corner_radius=8,
                                           border_color=BORDER, fg_color="#f8fafc",
                                           text_color=TEXT_PRIMARY, button_color=ORANGE)
        self._combo_loai.pack(fill="x")
        self._combo_loai.set(s.loai if s else LOAI_SAN[0])

        # Trạng thái
        ctk.CTkLabel(than, text="TRẠNG THÁI", font=ctk.CTkFont(size=9, weight="bold"),
                     text_color=TEXT_MUTED, anchor="w").pack(fill="x", pady=(8, 2))
        _TT_HIEN_F = {"ACTIVE": "Hoạt động", "INACTIVE": "Vô hiệu"}
        _TT_DB_F   = {v: k for k, v in _TT_HIEN_F.items()}
        _tt_init_f = _TT_HIEN_F.get(s.trang_thai, "Hoạt động") if s else "Hoạt động"
        self._bien_tt_f = ctk.StringVar(value=_tt_init_f)
        self._tt_db_map_f = _TT_DB_F
        self._combo_tt = ctk.CTkComboBox(than, values=list(_TT_HIEN_F.values()),
                                         variable=self._bien_tt_f,
                                         height=40, corner_radius=8,
                                         border_color=BORDER, fg_color="#f8fafc",
                                         text_color=TEXT_PRIMARY, button_color=ORANGE)
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
            self.app.hien_thong_bao("Tên sân/phòng không được để trống", "error")
            return
        try:
            suc_chua = int(self._suc_chua.get().strip() or "0")
        except ValueError:
            suc_chua = 0
        data = {
            "ten": ten, "loai": self._combo_loai.get(),
            "vi_tri": self._vi_tri.get().strip(),
            "suc_chua": suc_chua, "trang_thai": self._tt_db_map_f.get(self._bien_tt_f.get(), self._bien_tt_f.get())
        }
        if self.san:
            data["__san__"] = self.san
        self.destroy()
        self.khi_luu(data)
