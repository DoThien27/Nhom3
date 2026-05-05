"""
Dashboard — Tổng quan hệ thống
"""
import matplotlib
import matplotlib.pyplot as plt
import customtkinter as ctk
from datetime import datetime, date
from ui.app import (ORANGE, ORANGE_LIGHT, WHITE, BG, TEXT_PRIMARY,
                     TEXT_SECONDARY, TEXT_MUTED, BORDER, EMERALD, RED, BLUE)


def _tron_mau_alpha(hex_color: str, alpha: float, bg: str = "#ffffff") -> str:
    """Blend hex_color over bg at given alpha (0-1) → returns solid #RRGGBB."""
    def parse(h):
        h = h.lstrip("#")
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    fr, fg, fb = parse(hex_color)
    br, bg_r, bb = parse(bg)
    r = int(fr * alpha + br * (1 - alpha))
    g = int(fg * alpha + bg_r * (1 - alpha))
    b = int(fb * alpha + bb * (1 - alpha))
    return f"#{r:02x}{g:02x}{b:02x}"

try:
    matplotlib.use("TkAgg")
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MPL = True
except ImportError:
    HAS_MPL = False


class TrangTongQuan(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, fg_color=BG, corner_radius=0, **kwargs)
        self.app = app
        self._canvas_list = []
        self._tao_giao_dien()

    def _lam_moi(self):
        """Gọi mỗi lần điều hướng tới dashboard — rebuild stats từ dữ liệu mới nhất."""
        for c in self._canvas_list:
            try:
                plt.close()
                c.get_tk_widget().destroy()
            except Exception:
                pass
        self._canvas_list.clear()
        for w in self.winfo_children():
            w.destroy()
        self._tao_giao_dien()

    def _tao_giao_dien(self):
        # Scrollable container
        cuon = ctk.CTkScrollableFrame(self, fg_color=BG, corner_radius=0,
                                         scrollbar_button_color=BORDER)
        cuon.pack(fill="both", expand=True, padx=0, pady=0)
        cuon.grid_columnconfigure((0, 1, 2, 3), weight=1)

        dashboard_data = self.app.du_lieu.get("dashboard", {})
        
        ngay_hom_nay = date.today().isoformat()
        active_members  = dashboard_data.get('tong_hoi_vien', 0)
        total_revenue   = dashboard_data.get('doanh_thu', 0.0)
        upcoming_events = len(dashboard_data.get('su_kien_sap_toi', []))
        so_hlv          = dashboard_data.get('tong_hlv', 0)
        so_mon          = dashboard_data.get('tong_mon', 0)
        so_lop          = dashboard_data.get('tong_lop', 0)
        events          = dashboard_data.get('su_kien_sap_toi', [])

        # === Stat Cards ===
        du_lieu_the = [
            ("👥 Hội Viên",          str(active_members), "Đang hoạt động",  BLUE,    "#eff6ff"),
            ("🏆 Môn Thể Thao",      str(so_mon),         "Môn đang mở",     ORANGE,  "#fff7ed"),
            ("⚽ Lớp/Buổi Tập",      str(so_lop),         "Tổng số lớp",     EMERALD, "#ecfdf5"),
            ("🎖️ Sự Kiện/Giải Đấu", str(upcoming_events),"Sắp diễn ra",     "#7c3aed","#f5f3ff"),
        ]
        hang_thong_ke = ctk.CTkFrame(cuon, fg_color=BG, corner_radius=0)
        hang_thong_ke.pack(fill="x", padx=24, pady=(24, 0))
        hang_thong_ke.grid_columnconfigure((0, 1, 2, 3), weight=1)

        for col, (tieu_de, gia_tri, phu, mau_nhan, bg_c) in enumerate(du_lieu_the):
            the = ctk.CTkFrame(hang_thong_ke, fg_color=WHITE, corner_radius=24,
                                 border_width=1, border_color=BORDER)
            the.grid(row=0, column=col, padx=10 if col < 3 else 0, pady=0, sticky="ew")

            ctk.CTkLabel(the, text=tieu_de,
                         font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                         text_color=TEXT_MUTED).pack(anchor="w", padx=24, pady=(24, 4))
            ctk.CTkLabel(the, text=gia_tri,
                         font=ctk.CTkFont(family="Inter", size=32, weight="bold"),
                         text_color=TEXT_PRIMARY).pack(anchor="w", padx=24)
            
            badge = ctk.CTkFrame(the, fg_color=bg_c, corner_radius=8)
            badge.pack(anchor="w", padx=24, pady=(8, 24))
            ctk.CTkLabel(badge, text=phu,
                         font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
                         text_color=mau_nhan).pack(padx=10, pady=4)

        # === Hàng 2: Stats doanh thu + HLV + Thao tác ===
        hang_1b = ctk.CTkFrame(cuon, fg_color=BG, corner_radius=0)
        hang_1b.pack(fill="x", padx=24, pady=(12, 0))
        hang_1b.grid_columnconfigure((0, 1), weight=1)

        the_dt = ctk.CTkFrame(hang_1b, fg_color=WHITE, corner_radius=24, border_width=1, border_color=BORDER)
        the_dt.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        ctk.CTkLabel(the_dt, text="💰 Doanh Thu",
                     font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_MUTED).pack(anchor="w", padx=24, pady=(20, 4))
        ctk.CTkLabel(the_dt, text=f"{total_revenue:,.0f} đ",
                     font=ctk.CTkFont(size=26, weight="bold"), text_color=TEXT_PRIMARY).pack(anchor="w", padx=24)
        badge2 = ctk.CTkFrame(the_dt, fg_color="#fff7ed", corner_radius=8)
        badge2.pack(anchor="w", padx=24, pady=(8, 20))
        ctk.CTkLabel(badge2, text="Tổng thu nhập", font=ctk.CTkFont(size=11, weight="bold"), text_color=ORANGE).pack(padx=10, pady=4)

        the_hlv = ctk.CTkFrame(hang_1b, fg_color=WHITE, corner_radius=24, border_width=1, border_color=BORDER)
        the_hlv.grid(row=0, column=1, sticky="ew")
        ctk.CTkLabel(the_hlv, text="🏅 Huấn Luyện Viên",
                     font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_MUTED).pack(anchor="w", padx=24, pady=(20, 4))
        ctk.CTkLabel(the_hlv, text=str(so_hlv),
                     font=ctk.CTkFont(size=26, weight="bold"), text_color=TEXT_PRIMARY).pack(anchor="w", padx=24)
        badge3 = ctk.CTkFrame(the_hlv, fg_color="#eff6ff", corner_radius=8)
        badge3.pack(anchor="w", padx=24, pady=(8, 20))
        ctk.CTkLabel(badge3, text="PT & Quản lý", font=ctk.CTkFont(size=11, weight="bold"), text_color=BLUE).pack(padx=10, pady=4)

        # === Chart + Quick Actions ===
        hang_2 = ctk.CTkFrame(cuon, fg_color=BG, corner_radius=0)
        hang_2.pack(fill="x", padx=24, pady=16)
        hang_2.grid_columnconfigure(0, weight=3)
        hang_2.grid_columnconfigure(1, weight=1)

        # Chart card
        the_bieu_do = ctk.CTkFrame(hang_2, fg_color=WHITE, corner_radius=20,
                                   border_width=1, border_color=BORDER)
        the_bieu_do.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        ctk.CTkLabel(the_bieu_do, text="Trạng Thái Hệ Thống",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=24, pady=(20, 4))
        ctk.CTkLabel(the_bieu_do, text=f"Hôm nay: {ngay_hom_nay}",
                     font=ctk.CTkFont(size=11), text_color=TEXT_SECONDARY).pack(anchor="w", padx=24, pady=(0, 12))

        khung_thong_tin = ctk.CTkFrame(the_bieu_do, fg_color="transparent")
        khung_thong_tin.pack(fill="both", expand=True, padx=24, pady=10)
        
        ctk.CTkLabel(khung_thong_tin, text="✅ Hệ thống hoạt động bình thường", font=ctk.CTkFont(weight="bold"), text_color=EMERALD).pack(anchor="w", pady=4)
        ctk.CTkLabel(khung_thong_tin, text=f"🎖️ Có {upcoming_events} sự kiện/giải đấu sắp diễn ra.", font=ctk.CTkFont(weight="bold"), text_color=BLUE).pack(anchor="w", pady=4)
        ctk.CTkLabel(khung_thong_tin, text=f"🏆 {so_mon} môn thể thao | ⚽ {so_lop} lớp/buổi tập | 🏅 {so_hlv} HLV", font=ctk.CTkFont(weight="bold"), text_color=ORANGE).pack(anchor="w", pady=4)


        # Quick actions card
        the_thao_tac = ctk.CTkFrame(hang_2, fg_color=WHITE, corner_radius=20,
                                 border_width=1, border_color=BORDER)
        the_thao_tac.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(the_thao_tac, text="Thao tác nhanh",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=20, pady=(20, 12))

        thao_tac = [
            ("🎖️ Sự Kiện/Giải Đấu", "Quản lý sự kiện", ORANGE, "events"),
            ("💳 Tạo Hóa Đơn",       "Bán hàng mới",    EMERALD, "billing"),
        ]
        for tieu_de, phu, mau, trang in thao_tac:
            khung_nut = ctk.CTkFrame(the_thao_tac,
                                      fg_color=_tron_mau_alpha(mau, 0.05),
                                      corner_radius=16, border_width=1,
                                      border_color=_tron_mau_alpha(mau, 0.15))
            khung_nut.pack(fill="x", padx=16, pady=6)
            khung_nut.bind("<Button-1>", lambda e, p=trang: self.app.dieu_huong(p))
            inner = ctk.CTkFrame(khung_nut, fg_color="transparent", corner_radius=0)
            inner.pack(fill="x", padx=16, pady=12)
            ctk.CTkLabel(inner, text=tieu_de,
                         font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                         text_color=TEXT_PRIMARY).pack(anchor="w")
            ctk.CTkLabel(inner, text=phu,
                         font=ctk.CTkFont(family="Inter", size=10, weight="bold"),
                         text_color=TEXT_MUTED).pack(anchor="w")



        # === Upcoming Events ===
        the_su_kien = ctk.CTkFrame(cuon, fg_color=WHITE, corner_radius=20,
                                 border_width=1, border_color=BORDER)
        the_su_kien.pack(fill="x", padx=24, pady=(0, 24))

        dau_trang = ctk.CTkFrame(the_su_kien, fg_color=WHITE, corner_radius=0)
        dau_trang.pack(fill="x", padx=24, pady=(20, 0))
        ctk.CTkLabel(dau_trang, text="Sự Kiện Sắp Tới",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(side="left")
        ctk.CTkButton(dau_trang, text="Xem toàn bộ →",
                      fg_color="transparent", text_color=TEXT_MUTED,
                      hover_color=ORANGE_LIGHT, font=ctk.CTkFont(size=11, weight="bold"),
                      height=28, corner_radius=8,
                      command=lambda: self.app.dieu_huong("events")).pack(side="right")

        sap_toi = sorted([e for e in events if e.trang_thai == "UPCOMING"], key=lambda e: e.ngay)[:9]
        if sap_toi:
            luoi = ctk.CTkFrame(the_su_kien, fg_color=WHITE, corner_radius=0)
            luoi.pack(fill="x", padx=20, pady=16)
            luoi.grid_columnconfigure((0, 1, 2), weight=1)
            for i, su_kien in enumerate(sap_toi):
                hang = i // 3
                cot = i % 3
                o = ctk.CTkFrame(luoi, fg_color=WHITE, corner_radius=16,
                                     border_width=1, border_color=BORDER)
                o.grid(row=hang, column=cot, padx=8, pady=8, sticky="ew")
                tren = ctk.CTkFrame(o, fg_color="transparent", corner_radius=0)
                tren.pack(fill="x", padx=16, pady=(16, 0))
                ctk.CTkLabel(tren, text=su_kien.ten.upper(),
                             font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                             text_color=TEXT_PRIMARY).pack(side="left")
                
                ctk.CTkLabel(o, text=f"📅 {su_kien.ngay} | ⏰ {su_kien.gio}",
                             font=ctk.CTkFont(family="Inter", size=11), text_color=TEXT_SECONDARY).pack(anchor="w", padx=16, pady=(8, 2))
                ctk.CTkLabel(o, text=f"📍 {su_kien.dia_diem} | 👥 Max: {su_kien.suc_chua}",
                             font=ctk.CTkFont(family="Inter", size=11), text_color=TEXT_SECONDARY).pack(anchor="w", padx=16, pady=(0, 16))
        else:
            ctk.CTkLabel(the_su_kien, text="Chưa có sự kiện nào sắp tới.",
                         font=ctk.CTkFont(size=12), text_color=TEXT_MUTED).pack(pady=40)
