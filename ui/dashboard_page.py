"""
Dashboard — Tổng quan hệ thống
"""
import customtkinter as ctk
from datetime import datetime, date
from ui.app import (ORANGE, ORANGE_LIGHT, WHITE, BG, TEXT_PRIMARY,
                     TEXT_SECONDARY, TEXT_MUTED, BORDER, EMERALD, RED, BLUE)


def _alpha_blend(hex_color: str, alpha: float, bg: str = "#ffffff") -> str:
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
    import matplotlib
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MPL = True
except ImportError:
    HAS_MPL = False


class DashboardPage(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, fg_color=BG, corner_radius=0, **kwargs)
        self.app = app
        self._build()

    def _build(self):
        # Scrollable container
        scroll = ctk.CTkScrollableFrame(self, fg_color=BG, corner_radius=0,
                                         scrollbar_button_color=BORDER)
        scroll.pack(fill="both", expand=True, padx=0, pady=0)
        scroll.grid_columnconfigure((0, 1, 2, 3), weight=1)

        members    = self.app.data.get("members", [])
        invoices   = self.app.data.get("invoices", [])
        events     = self.app.data.get("events", [])
        products   = self.app.data.get("products", [])

        today_str = date.today().isoformat()
        active_members  = sum(1 for m in members if m.status == "ACTIVE")
        total_revenue   = sum(inv.total for inv in invoices)
        upcoming_events = sum(1 for e in events if e.status == "UPCOMING")
        low_stock       = sum(1 for p in products if p.stock <= p.minStockAlert)

        # === Stat Cards ===
        card_data = [
            ("👥 Hội Viên", str(active_members), "Đang hoạt động", BLUE, "#eff6ff"),
            ("💰 Doanh Thu", f"{total_revenue:,.0f} đ", "Tổng thu nhập", ORANGE, "#fff7ed"),
            ("🎉 Sự Kiện", str(upcoming_events), "Sắp diễn ra", EMERALD, "#ecfdf5"),
            ("📦 Kho hàng", str(low_stock), "Cần nhập hàng", RED, "#fef2f2"),
        ]
        stat_row = ctk.CTkFrame(scroll, fg_color=BG, corner_radius=0)
        stat_row.pack(fill="x", padx=24, pady=(24, 0))
        stat_row.grid_columnconfigure((0, 1, 2, 3), weight=1)

        for col, (title, value, sub, accent, bg_c) in enumerate(card_data):
            card = ctk.CTkFrame(stat_row, fg_color=WHITE, corner_radius=20,
                                 border_width=1, border_color=BORDER)
            card.grid(row=0, column=col, padx=8 if col < 3 else 0, pady=0, sticky="ew")

            ctk.CTkLabel(card, text=title,
                         font=ctk.CTkFont(size=10, weight="bold"),
                         text_color=TEXT_MUTED).pack(anchor="w", padx=20, pady=(18, 0))
            ctk.CTkLabel(card, text=value,
                         font=ctk.CTkFont(size=28, weight="bold"),
                         text_color=TEXT_PRIMARY).pack(anchor="w", padx=20)
            ctk.CTkLabel(card, text=sub,
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=accent).pack(anchor="w", padx=20, pady=(0, 18))

        # === Chart + Quick Actions ===
        row2 = ctk.CTkFrame(scroll, fg_color=BG, corner_radius=0)
        row2.pack(fill="x", padx=24, pady=16)
        row2.grid_columnconfigure(0, weight=3)
        row2.grid_columnconfigure(1, weight=1)

        # Chart card
        chart_card = ctk.CTkFrame(row2, fg_color=WHITE, corner_radius=20,
                                   border_width=1, border_color=BORDER)
        chart_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        ctk.CTkLabel(chart_card, text="Trạng Thái Hệ Thống",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=24, pady=(20, 4))
        ctk.CTkLabel(chart_card, text=f"Hôm nay: {today_str}",
                     font=ctk.CTkFont(size=11), text_color=TEXT_SECONDARY).pack(anchor="w", padx=24, pady=(0, 12))

        info_frame = ctk.CTkFrame(chart_card, fg_color="transparent")
        info_frame.pack(fill="both", expand=True, padx=24, pady=10)
        
        ctk.CTkLabel(info_frame, text="✅ Hệ thống hoạt động bình thường", font=ctk.CTkFont(weight="bold"), text_color=EMERALD).pack(anchor="w", pady=4)
        ctk.CTkLabel(info_frame, text=f"🎉 Có {upcoming_events} sự kiện sắp diễn ra.", font=ctk.CTkFont(weight="bold"), text_color=BLUE).pack(anchor="w", pady=4)


        # Quick actions card
        qa_card = ctk.CTkFrame(row2, fg_color=WHITE, corner_radius=20,
                                border_width=1, border_color=BORDER)
        qa_card.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(qa_card, text="Thao tác nhanh",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=20, pady=(20, 12))

        actions = [
            ("🎉 Sự Kiện", "Quản lý sự kiện", ORANGE, "events"),
            ("💳 Tạo Hóa Đơn", "Bán hàng mới", EMERALD, "billing"),
            ("👥 Hội Viên", "Quản lý thành viên", BLUE, "members"),
        ]
        for label, sub, color, page in actions:
            btn_frame = ctk.CTkFrame(qa_card,
                                      fg_color=_alpha_blend(color, 0.09),
                                      corner_radius=14, border_width=1,
                                      border_color=_alpha_blend(color, 0.19))
            btn_frame.pack(fill="x", padx=12, pady=4)
            btn_frame.bind("<Button-1>", lambda e, p=page: self.app.navigate(p))
            inner = ctk.CTkFrame(btn_frame, fg_color="transparent", corner_radius=0)
            inner.pack(fill="x", padx=12, pady=10)
            ctk.CTkLabel(inner, text=label,
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=TEXT_PRIMARY).pack(anchor="w")
            ctk.CTkLabel(inner, text=sub,
                         font=ctk.CTkFont(size=9, weight="bold"),
                         text_color=TEXT_MUTED).pack(anchor="w")

        if low_stock:
            warn = ctk.CTkFrame(qa_card, fg_color="#0f172a", corner_radius=14)
            warn.pack(fill="x", padx=12, pady=(8, 12))
            ctk.CTkLabel(warn, text=f"⚠ {low_stock} mặt hàng cần nhập kho",
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=ORANGE).pack(padx=14, pady=(12, 4))
            ctk.CTkButton(warn, text="Xem chi tiết →",
                          fg_color=_alpha_blend("#ffffff", 0.09, "#0f172a"),
                          hover_color=_alpha_blend("#ffffff", 0.19, "#0f172a"),
                          text_color=WHITE, font=ctk.CTkFont(size=10, weight="bold"),
                          corner_radius=8, height=28,
                          command=lambda: self.app.navigate("inventory")).pack(padx=14, pady=(0, 12), anchor="w")

        # === Upcoming Events ===
        act_card = ctk.CTkFrame(scroll, fg_color=WHITE, corner_radius=20,
                                 border_width=1, border_color=BORDER)
        act_card.pack(fill="x", padx=24, pady=(0, 24))

        header = ctk.CTkFrame(act_card, fg_color=WHITE, corner_radius=0)
        header.pack(fill="x", padx=24, pady=(20, 0))
        ctk.CTkLabel(header, text="Sự Kiện Sắp Tới",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(side="left")
        ctk.CTkButton(header, text="Xem toàn bộ →",
                      fg_color="transparent", text_color=TEXT_MUTED,
                      hover_color=ORANGE_LIGHT, font=ctk.CTkFont(size=11, weight="bold"),
                      height=28, corner_radius=8,
                      command=lambda: self.app.navigate("events")).pack(side="right")

        recent = sorted([e for e in events if e.status == "UPCOMING"], key=lambda e: e.date)[:9]
        if recent:
            grid = ctk.CTkFrame(act_card, fg_color=WHITE, corner_radius=0)
            grid.pack(fill="x", padx=20, pady=16)
            grid.grid_columnconfigure((0, 1, 2), weight=1)
            for i, event in enumerate(recent):
                row = i // 3
                col = i % 3
                cell = ctk.CTkFrame(grid, fg_color="#f8fafc", corner_radius=14,
                                     border_width=1, border_color=BORDER)
                cell.grid(row=row, column=col, padx=6, pady=6, sticky="ew")
                top = ctk.CTkFrame(cell, fg_color="transparent", corner_radius=0)
                top.pack(fill="x", padx=12, pady=(10, 0))
                ctk.CTkLabel(top, text=event.name.upper(),
                             font=ctk.CTkFont(size=11, weight="bold"),
                             text_color=TEXT_PRIMARY).pack(side="left")
                
                ctk.CTkLabel(cell, text=f"📅 {event.date} | ⏰ {event.time}",
                             font=ctk.CTkFont(size=10), text_color=TEXT_SECONDARY).pack(anchor="w", padx=12, pady=(4, 2))
                ctk.CTkLabel(cell, text=f"📍 {event.location} | 👥 Max: {event.capacity}",
                             font=ctk.CTkFont(size=10), text_color=TEXT_SECONDARY).pack(anchor="w", padx=12, pady=(0, 10))
        else:
            ctk.CTkLabel(act_card, text="Chưa có sự kiện nào sắp tới.",
                         font=ctk.CTkFont(size=12), text_color=TEXT_MUTED).pack(pady=40)

