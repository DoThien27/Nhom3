"""
Main Application Window — Hệ thống Quản lý CLB Thể Thao
Layout: Sidebar (trai) + Content area (phai)
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
import importlib
import customtkinter as ctk
from datetime import datetime
from typing import Optional
import threading

# Color palette
ORANGE = "#ea580c"
ORANGE_DARK = "#c2410c"
ORANGE_LIGHT = "#ffedd5"
BG = "#f1f5f9"
WHITE = "#ffffff"
SIDEBAR_BG = "#ffffff"
TEXT_PRIMARY = "#0f172a"
TEXT_SECONDARY = "#475569"
TEXT_MUTED = "#94a3b8"
BORDER = "#e2e8f0"
EMERALD = "#059669"
RED = "#dc2626"
BLUE = "#2563eb"
SLATE_900 = "#0f172a"

# Role → accessible pages
ROLE_MENU = {
    "ADMIN":        ["dashboard", "members", "trainers", "sports", "classes", "facilities",
                     "events", "billing", "reports", "system_users"],
    "MANAGER":      ["dashboard", "members", "trainers", "sports", "classes", "facilities",
                     "events", "billing", "reports"],
    "RECEPTIONIST": ["members", "classes", "facilities", "events", "billing"],
    "PT":           ["members", "classes"],
    "MEMBER":       ["classes"],
}

MENU_LABELS = {
    "dashboard":    "Tổng quan",
    "members":      "Hội viên",
    "trainers":     "Huấn luyện viên",
    "sports":       "Môn thể thao",
    "classes":      "Lớp/Buổi tập",
    "facilities":   "Sân bãi/Phòng tập",
    "events":       "Sự kiện/Giải đấu",
    "billing":      "Tài chính & Hóa đơn",
    "reports":      "Báo cáo",
    "system_users": "Hệ thống",
}

MENU_ICONS = {
    "dashboard":    "📊",
    "members":      "👥",
    "trainers":     "🏅",
    "sports":       "🏆",
    "classes":      "⚽",
    "facilities":   "🏟️",
    "events":       "🎖️",
    "billing":      "💳",
    "reports":      "📈",
    "system_users": "⚙️",
}


class UngDungCauLacBo(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.title("Phần mềm quản lý câu lạc bộ thể thao")
        w, h = 1366, 768
        self.geometry(f"{w}x{h}")
        self.update_idletasks()
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws - w) // 2
        y = (hs - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.minsize(1024, 640)
        self.configure(fg_color=BG)

        # State
        self.nguoi_dung_hien_tai = None
        self.ma_trang_hien_tai: Optional[str] = None
        self._bo_nho_dem_trang: dict = {}
        self._debounce_timers: dict = {}  # Lưu trữ các timer để chống lag khi gõ tìm kiếm
        self._dang_tai_du_lieu: bool = False  # Flag tránh load DB 2 lần đồng thời

        # Data store (loaded once, shared across pages)
        self.du_lieu = {
            "members": [],
            "plans": [],
            "classes": [],
            "invoices": [],
            "events": [],
            "users": [],
            "sports": [],
            "facilities": [],
        }
        self.du_lieu_revision = 0

        # Warm-up DB connections sẵn ngay khi app khởi động (trước khi login)
        from database.db_connection import warm_up as db_warm_up
        db_warm_up()

        self._tao_bo_khung()
        self._hien_dang_nhap()

    # ------------------------------------------------------------------
    # Layout builders
    # ------------------------------------------------------------------
    def _tao_bo_khung(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.thanh_ben = ctk.CTkFrame(self, width=260, fg_color=SIDEBAR_BG,
                                    corner_radius=0, border_width=0,
                                    border_color=BORDER)
        self.thanh_ben.grid(row=0, column=0, sticky="nsw")
        self.thanh_ben.grid_propagate(False)
        # Thêm border phải bằng frame mỏng
        ctk.CTkFrame(self, width=1, fg_color=BORDER, corner_radius=0).grid(
            row=0, column=0, sticky="nse")

        self._tao_logo_thanh_ben()
        self._tao_panel_nguoi_dung()   # Pack user panel trước (side=bottom)
        self._tao_thanh_dieu_huong()   # Nav fill phần còn lại (side=top, expand)

        # Main content
        self.vung_noi_dung = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        self.vung_noi_dung.grid(row=0, column=1, sticky="nsew")
        self.vung_noi_dung.grid_rowconfigure(1, weight=1)
        self.vung_noi_dung.grid_columnconfigure(0, weight=1)

        self._tao_thanh_tren()

        self.khung_noi_dung = ctk.CTkFrame(self.vung_noi_dung, fg_color=BG, corner_radius=0)
        self.khung_noi_dung.grid(row=1, column=0, sticky="nsew")
        self.khung_noi_dung.grid_rowconfigure(0, weight=1)
        self.khung_noi_dung.grid_columnconfigure(0, weight=1)

        # Notification overlay
        self._danh_sach_nhan_thong_bao = []

        # Initially hide sidebar until login
        self.thanh_ben.grid_remove()
        self.vung_noi_dung.grid_remove()

        # Login frame overlay
        self.khung_dang_nhap = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        self.khung_dang_nhap.grid(row=0, column=0, columnspan=2, sticky="nsew")

    def _tao_logo_thanh_ben(self):
        khung_logo = ctk.CTkFrame(self.thanh_ben, fg_color=SIDEBAR_BG,
                                   height=72, corner_radius=0)
        khung_logo.pack(side="top", fill="x")
        khung_logo.grid_propagate(False)
        khung_logo.grid_columnconfigure(0, weight=1)

        inner = ctk.CTkFrame(khung_logo, fg_color=SIDEBAR_BG, corner_radius=0)
        inner.pack(fill="both", expand=True, padx=20)

        icon_box = ctk.CTkLabel(inner, text="🏆", font=ctk.CTkFont(size=24),
                                 fg_color=ORANGE, corner_radius=10,
                                 width=40, height=40)
        icon_box.pack(side="left", pady=16)

        text_frame = ctk.CTkFrame(inner, fg_color=SIDEBAR_BG, corner_radius=0)
        text_frame.pack(side="left", padx=(10, 0), pady=16)
        ctk.CTkLabel(text_frame, text="CLB Thể Thao",
                     font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(text_frame, text="MANAGEMENT",
                     font=ctk.CTkFont(family="Inter", size=9, weight="bold"),
                     text_color=ORANGE).pack(anchor="w")

    def _tao_thanh_dieu_huong(self):
        self.khung_dieu_huong = ctk.CTkScrollableFrame(self.thanh_ben, fg_color=SIDEBAR_BG,
                                             corner_radius=0, scrollbar_button_color=BORDER)
        self.khung_dieu_huong.pack(side="top", fill="both", expand=True, padx=0, pady=(4, 4))
        self.cac_nut_dieu_huong: dict = {}

    def _tao_panel_nguoi_dung(self):
        # Separator dòng ngang trên user panel
        ctk.CTkFrame(self.thanh_ben, fg_color=BORDER, height=1,
                     corner_radius=0).pack(side="bottom", fill="x")

        self.panel_nguoi_dung = ctk.CTkFrame(
            self.thanh_ben, fg_color=SIDEBAR_BG, corner_radius=0)
        # side=bottom → luôn ghim dưới cùng, không phụ thuộc số menu
        self.panel_nguoi_dung.pack(side="bottom", fill="x")
        self.panel_nguoi_dung.grid_columnconfigure(1, weight=1)

        self.nhan_avatar_nguoi_dung = ctk.CTkLabel(self.panel_nguoi_dung, text="?",
                                              font=ctk.CTkFont(size=16, weight="bold"),
                                              fg_color="#fed7aa", text_color=ORANGE,
                                              corner_radius=10, width=40, height=40)
        self.nhan_avatar_nguoi_dung.grid(row=0, column=0, sticky="w", padx=16, pady=(14, 6))

        self.nhan_ten_nguoi_dung = ctk.CTkLabel(self.panel_nguoi_dung, text="",
                                            font=ctk.CTkFont(size=13, weight="bold"),
                                            text_color=TEXT_PRIMARY)
        self.nhan_ten_nguoi_dung.grid(row=0, column=1, sticky="w", padx=(0, 16))

        self.nhan_vai_tro_nguoi_dung = ctk.CTkLabel(self.panel_nguoi_dung, text="",
                                           font=ctk.CTkFont(size=10, weight="bold"),
                                           text_color=ORANGE)
        self.nhan_vai_tro_nguoi_dung.grid(row=1, column=1, sticky="w", padx=(0, 16))

        nut_dang_xuat = ctk.CTkButton(self.panel_nguoi_dung, text="⟵  Đăng xuất",
                                    font=ctk.CTkFont(size=11, weight="bold"),
                                    fg_color="transparent", text_color=TEXT_MUTED,
                                    hover_color="#fef2f2",
                                    command=self._xac_nhan_dang_xuat, anchor="w",
                                    height=32, corner_radius=8)
        nut_dang_xuat.grid(row=2, column=0, columnspan=2, sticky="ew",
                        padx=12, pady=(4, 12))

    def _tao_thanh_tren(self):
        self.thanh_tren = ctk.CTkFrame(self.vung_noi_dung, fg_color=WHITE,
                                    corner_radius=0, height=60,
                                    border_width=1, border_color=BORDER)
        self.thanh_tren.grid(row=0, column=0, sticky="ew")
        self.thanh_tren.grid_propagate(False)
        self.thanh_tren.grid_columnconfigure(1, weight=1)

        self.nhan_tieu_de_trang = ctk.CTkLabel(self.thanh_tren, text="",
                                            font=ctk.CTkFont(size=16, weight="bold"),
                                            text_color=TEXT_PRIMARY)
        self.nhan_tieu_de_trang.grid(row=0, column=0, padx=24, pady=0, sticky="w")

        ngay_hien_tai = datetime.now().strftime("%a, %d/%m/%Y")
        khung_ngay = ctk.CTkFrame(self.thanh_tren, fg_color=WHITE, corner_radius=20,
                                   border_width=1, border_color=BORDER)
        khung_ngay.grid(row=0, column=2, padx=16, pady=10, sticky="e")
        ctk.CTkLabel(khung_ngay, text=f"● {ngay_hien_tai}",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=TEXT_SECONDARY).pack(padx=16, pady=4)

    # ------------------------------------------------------------------
    # Login flow
    # ------------------------------------------------------------------
    def _hien_dang_nhap(self):
        from ui.login_page import TrangDangNhap
        for w in self.khung_dang_nhap.winfo_children():
            w.destroy()
        TrangDangNhap(self.khung_dang_nhap, khi_dang_nhap_thanh_cong=self._khi_dang_nhap).pack(fill="both", expand=True)
        self.khung_dang_nhap.grid()
        self.thanh_ben.grid_remove()
        self.vung_noi_dung.grid_remove()

    def _khi_dang_nhap(self, nguoi_dung):
        self.nguoi_dung_hien_tai = nguoi_dung
        self.khung_dang_nhap.grid_remove()

        # Update user panel
        chu_cai_dau = "".join(w[0] for w in nguoi_dung.ho_ten.split() if w)[:2].upper()
        self.nhan_avatar_nguoi_dung.configure(text=chu_cai_dau)
        self.nhan_ten_nguoi_dung.configure(text=nguoi_dung.ho_ten)
        self.nhan_vai_tro_nguoi_dung.configure(text=nguoi_dung.vai_tro)

        # Build nav
        self._tao_thanh_dieu_huong_chi_tiet()

        # Show layout
        self.thanh_ben.grid()
        self.vung_noi_dung.grid()
        self.thanh_ben.grid_columnconfigure(0, weight=1)

        # Full màn hình khi đăng nhập
        self.state("zoomed")

        # Điều hướng đến trang đầu trước để UI hiển thị ngay
        pages = ROLE_MENU.get(nguoi_dung.vai_tro, [])
        if pages:
            self.dieu_huong(pages[0])

        # Load dữ liệu của trang đầu tiên được tự động xử lý bên trong dieu_huong()

    def _tao_thanh_dieu_huong_chi_tiet(self):
        for w in self.khung_dieu_huong.winfo_children():
            w.destroy()
        self.cac_nut_dieu_huong.clear()
        pages = ROLE_MENU.get(self.nguoi_dung_hien_tai.vai_tro, [])
        for key in pages:
            icon = MENU_ICONS.get(key, "•")
            label = MENU_LABELS.get(key, key)
            
            btn_frame = ctk.CTkFrame(self.khung_dieu_huong, fg_color="transparent", corner_radius=12, height=46)
            btn_frame.pack(fill="x", pady=3, padx=10)
            btn_frame.pack_propagate(False)
            
            lbl_icon = ctk.CTkLabel(btn_frame, text=icon, font=ctk.CTkFont(size=16), width=24, anchor="w", text_color=TEXT_SECONDARY)
            lbl_icon.place(x=16, rely=0.5, anchor="w")
            
            lbl_text = ctk.CTkLabel(btn_frame, text=label, font=ctk.CTkFont(family="Inter", size=13, weight="bold"), text_color=TEXT_SECONDARY, anchor="w")
            lbl_text.place(x=54, rely=0.5, anchor="w", relwidth=0.7)

            def tao_su_kien(f, i_lbl, t_lbl, k):
                def on_enter(e):
                    if self.ma_trang_hien_tai != k:
                        f.configure(fg_color=ORANGE_LIGHT)
                        f.configure(cursor="hand2")
                        i_lbl.configure(cursor="hand2")
                        t_lbl.configure(cursor="hand2")
                def on_leave(e):
                    if self.ma_trang_hien_tai != k:
                        f.configure(fg_color="transparent")
                def on_click(e):
                    self.dieu_huong(k)
                for w in (f, i_lbl, t_lbl):
                    w.bind("<Enter>", on_enter)
                    w.bind("<Leave>", on_leave)
                    w.bind("<Button-1>", on_click)
                    
            tao_su_kien(btn_frame, lbl_icon, lbl_text, key)
            self.cac_nut_dieu_huong[key] = (btn_frame, lbl_icon, lbl_text)

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------
    def dieu_huong(self, ma_trang: str):
        if self.ma_trang_hien_tai == ma_trang:
            return
        self.ma_trang_hien_tai = ma_trang

        # Update nav highlight
        for k, widgets in self.cac_nut_dieu_huong.items():
            f, l_icon, l_text = widgets
            if k == ma_trang:
                f.configure(fg_color=ORANGE)
                l_icon.configure(text_color=WHITE)
                l_text.configure(text_color=WHITE)
            else:
                f.configure(fg_color="transparent")
                l_icon.configure(text_color=TEXT_SECONDARY)
                l_text.configure(text_color=TEXT_SECONDARY)

        # Update topbar title
        self.nhan_tieu_de_trang.configure(text=MENU_LABELS.get(ma_trang, ""))

        # Clear old page
        for w in self.khung_noi_dung.winfo_children():
            w.pack_forget()

        # Build new page if not cached
        if ma_trang not in self._bo_nho_dem_trang:
            page_cls = self._lay_lop_giao_dien(ma_trang)
            if page_cls:
                page = page_cls(self.khung_noi_dung, app=self)
                self._bo_nho_dem_trang[ma_trang] = page
        
        if ma_trang in self._bo_nho_dem_trang:
            page = self._bo_nho_dem_trang[ma_trang]
            page.pack(fill="both", expand=True)
            
            def _lam_moi_sau():
                page_rev = getattr(page, "_last_revision", -1)
                if page_rev == self.du_lieu_revision:
                    return
                page._last_revision = self.du_lieu_revision
                
                if hasattr(page, '_lam_moi_danh_sach'):
                    page._lam_moi_danh_sach()
                elif hasattr(page, '_lam_moi_bang'):
                    page._lam_moi_bang()
                elif hasattr(page, '_tai_su_kien'):
                    page._tai_su_kien()
                elif hasattr(page, '_lam_moi'):
                    page._lam_moi()
                elif hasattr(page, '_tao_giao_dien'):
                    pass

            mapping_keys = {
                "dashboard": ["dashboard"],
                "members": ["members", "plans", "users"],
                "trainers": ["users", "members"],
                "sports": ["sports"],
                "classes": ["classes", "users"],
                "facilities": ["facilities"],
                "events": ["events"],
                "billing": ["invoices", "members", "plans", "classes", "facilities", "events"],
                "reports": ["reports"],
                "system_users": ["users"]
            }
            keys = mapping_keys.get(ma_trang, [ma_trang])
            self.load_module_data(keys, force_refresh=False, on_complete=lambda: self.after(5, _lam_moi_sau))

    def _lay_lop_giao_dien(self, key: str):
        mapping = {
            "dashboard":    ("ui.dashboard_page",       "TrangTongQuan"),
            "members":      ("ui.members_page",          "TrangHoiVien"),
            "events":       ("ui.events_page",           "TrangSuKien"),
            "classes":      ("ui.classes_page",          "TrangLopHoc"),
            "billing":      ("ui.billing_page",          "TrangTaiChinh"),
            "trainers":     ("ui.trainers_page",         "TrangHuanLuyenVien"),
            "reports":      ("ui.reports_page",          "TrangBaoCao"),
            "system_users": ("ui.user_management_page",  "TrangQuanLyNhanSu"),
            "sports":       ("ui.sports_page",           "TrangMonTheThao"),
            "facilities":   ("ui.facilities_page",       "TrangSanBai"),
        }
        if key not in mapping:
            return None
        mod_name, cls_name = mapping[key]
        mod = importlib.import_module(mod_name)
        return getattr(mod, cls_name)

    def debounce(self, key, func, delay=300):
        """Trì hoãn thực thi func để tránh gọi quá nhiều lần (dùng cho tìm kiếm)"""
        if key in self._debounce_timers:
            self.after_cancel(self._debounce_timers[key])
        self._debounce_timers[key] = self.after(delay, func)

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------
    def load_module_data(self, keys: list, force_refresh: bool = False, on_complete=None):
        """Tải dữ liệu cho các module cụ thể."""
        if self._dang_tai_du_lieu:
            # Nếu đang tải, cứ gọi on_complete (tạm chấp nhận để tránh lock)
            if on_complete: self.after(100, on_complete)
            return
            
        self._dang_tai_du_lieu = True

        def _worker():
            import services.member_service as ms
            import services.plan_service as ps
            import services.class_service as cs
            import services.invoice_service as ivs
            import services.user_service as us
            import services.event_service as evs
            import services.sport_service as sps
            import services.facility_service as fs
            import services.dashboard_service as ds # service mới sẽ tạo

            tasks = {
                "members":    ms.lay_tat_ca,
                "plans":      ps.lay_tat_ca,
                "classes":    cs.lay_tat_ca,
                "invoices":   ivs.lay_tat_ca,
                "users":      us.lay_tat_ca,
                "events":     evs.lay_tat_ca_su_kien,
                "sports":     sps.lay_tat_ca,
                "facilities": fs.lay_tat_ca,
                "dashboard":  ds.lay_kpi_tong_quan if hasattr(ds, 'lay_kpi_tong_quan') else lambda: {},
                "reports":    ds.lay_bao_cao_tong_hop if hasattr(ds, 'lay_bao_cao_tong_hop') else lambda: {},
            }

            du_lieu_moi = {}
            loi = None
            
            # Chỉ tải những key yêu cầu (hoặc chưa có trong cache)
            keys_to_load = [k for k in keys if force_refresh or not self.du_lieu.get(k)]

            if keys_to_load:
                with ThreadPoolExecutor(max_workers=len(keys_to_load)) as pool:
                    future_to_key = {pool.submit(tasks[k]): k for k in keys_to_load if k in tasks}
                    for future in as_completed(future_to_key):
                        k = future_to_key[future]
                        try:
                            du_lieu_moi[k] = future.result()
                        except Exception as e:
                            du_lieu_moi[k] = []
                            loi = e

            def _cap_nhat():
                if du_lieu_moi:
                    self.du_lieu.update(du_lieu_moi)
                    self.du_lieu_revision += 1
                self._dang_tai_du_lieu = False
                if loi:
                    self.hien_thong_bao(f"Lỗi tải dữ liệu: {loi}", "error")
                if on_complete:
                    on_complete()
            self.after(0, _cap_nhat)

        threading.Thread(target=_worker, daemon=True).start()

    def refresh_module_data(self, keys: list):
        key = self.ma_trang_hien_tai
        def _sau_khi_tai_xong():
            if key in self._bo_nho_dem_trang:
                page = self._bo_nho_dem_trang[key]
                page._last_revision = self.du_lieu_revision
                if hasattr(page, '_lam_moi_danh_sach'):
                    page._lam_moi_danh_sach()
                elif hasattr(page, '_lam_moi_bang'):
                    page._lam_moi_bang()
                elif hasattr(page, '_tai_su_kien'):
                    page._tai_su_kien()
                elif hasattr(page, '_lam_moi'):
                    page._lam_moi()

        self.load_module_data(keys, force_refresh=True, on_complete=_sau_khi_tai_xong)

    def invalidate_module_cache(self, key: str):
        """Xóa cache của một module."""
        if key in self.du_lieu:
            self.du_lieu[key] = []
        self.du_lieu_revision += 1
        
    def lam_moi_du_lieu(self):
        """Hàm tương thích ngược: nạp lại module của trang hiện tại."""
        key = self.ma_trang_hien_tai
        if not key: return
        
        # Ánh xạ từ ma_trang sang keys cần thiết
        mapping = {
            "dashboard": ["dashboard"],
            "members": ["members", "plans", "users"],
            "trainers": ["users", "members"],
            "sports": ["sports"],
            "classes": ["classes", "users"],
            "facilities": ["facilities"],
            "events": ["events"],
            "billing": ["invoices", "members", "plans", "classes", "facilities", "events"],
            "reports": ["reports"],
            "system_users": ["users"]
        }
        keys = mapping.get(key, [key])
        self.refresh_module_data(keys)

    # ------------------------------------------------------------------
    # Notifications
    # ------------------------------------------------------------------
    def hien_thong_bao(self, thong_diep: str, loai_tb: str = "info"):
        self._danh_sach_nhan_thong_bao = [n for n in self._danh_sach_nhan_thong_bao if n.winfo_exists()]
        
        colors = {
            "success": ("#ecfdf5", EMERALD),
            "error":   ("#fef2f2", RED),
            "info":    ("#eff6ff", BLUE),
        }
        bg, accent = colors.get(loai_tb, colors["info"])
        icons = {"success": "✓", "error": "✕", "info": "ℹ"}
        icon = icons.get(loai_tb, "ℹ")

        target = self
        focus_widget = self.focus_get()
        if focus_widget:
            try:
                top = focus_widget.winfo_toplevel()
                if isinstance(top, ctk.CTkToplevel):
                    target = top
            except Exception:
                pass

        notif = ctk.CTkFrame(target, fg_color=bg, corner_radius=12,
                               border_width=2, border_color=accent)
        notif.place(relx=1.0, rely=0.0, anchor="ne",
                    x=-20, y=20 + len(self._danh_sach_nhan_thong_bao) * 70)
        ctk.CTkLabel(notif, text=f"{icon}  {thong_diep}",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=accent).pack(padx=16, pady=10)

        self._danh_sach_nhan_thong_bao.append(notif)
        self.after(3000, lambda: self._xoa_thong_bao(notif))

    def _xoa_thong_bao(self, notif):
        try:
            notif.place_forget()
            notif.destroy()
            if notif in self._danh_sach_nhan_thong_bao:
                self._danh_sach_nhan_thong_bao.remove(notif)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Logout
    # ------------------------------------------------------------------
    def _xac_nhan_dang_xuat(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Đăng xuất")
        w, h = 360, 220
        dialog.geometry(f"{w}x{h}")
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - w) // 2

        y = (dialog.winfo_screenheight() - h) // 2

        dialog.geometry(f"+{x}+{y}")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.focus_set()
        dialog.configure(fg_color=WHITE)

        ctk.CTkLabel(dialog, text="🚪", font=ctk.CTkFont(size=40)).pack(pady=(28, 4))
        ctk.CTkLabel(dialog, text="Đăng xuất khỏi hệ thống?",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT_PRIMARY).pack()
        ctk.CTkLabel(dialog, text="Bạn có chắc muốn thoát không?",
                     font=ctk.CTkFont(size=11), text_color=TEXT_SECONDARY).pack(pady=(4, 20))

        btn_frame = ctk.CTkFrame(dialog, fg_color=WHITE, corner_radius=0)
        btn_frame.pack(fill="x", padx=24)
        ctk.CTkButton(btn_frame, text="Hủy", fg_color="#f1f5f9",
                       text_color=TEXT_SECONDARY, hover_color=BORDER,
                       font=ctk.CTkFont(weight="bold"),
                       command=dialog.destroy).pack(side="left", expand=True, fill="x", padx=(0, 6))
        ctk.CTkButton(btn_frame, text="Đăng xuất", fg_color=RED,
                       hover_color="#dc2626", text_color=WHITE,
                       font=ctk.CTkFont(weight="bold"),
                       command=lambda: [dialog.destroy(), self._thuc_hien_dang_xuat()]).pack(side="left", expand=True, fill="x", padx=(6, 0))

    def _thuc_hien_dang_xuat(self):
        self.state("normal")
        self.nguoi_dung_hien_tai = None
        self.ma_trang_hien_tai = None
        self._bo_nho_dem_trang.clear()
        self.du_lieu = {k: [] for k in self.du_lieu}
        self._hien_dang_nhap()
