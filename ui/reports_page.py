"""
Báo cáo — Reports Page
"""
import customtkinter as ctk
from datetime import date, timedelta
from collections import defaultdict
from ui.app import (ORANGE, WHITE, BG, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
                     BORDER, EMERALD, RED, BLUE)

try:
    import matplotlib
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MPL = True
except ImportError:
    HAS_MPL = False


class ReportsPage(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, fg_color=BG, corner_radius=0, **kwargs)
        self.app = app
        self._build()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color=BG, corner_radius=0,
                                         scrollbar_button_color=BORDER)
        scroll.pack(fill="both", expand=True)

        ctk.CTkLabel(scroll, text="BÁO CÁO",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=24, pady=(20, 0))
        ctk.CTkLabel(scroll, text="Thống kê tổng hợp hệ thống",
                     font=ctk.CTkFont(size=11), text_color=TEXT_MUTED).pack(anchor="w", padx=24)

        invoices   = self.app.data["invoices"]
        members    = self.app.data["members"]
        attendance = self.app.data["attendance"]

        # === Summary stats ===
        total_rev   = sum(i.total for i in invoices)
        active_m    = sum(1 for m in members if m.status == "ACTIVE")
        expired_m   = sum(1 for m in members if m.status == "EXPIRED")
        total_att   = len(attendance)

        stats_frame = ctk.CTkFrame(scroll, fg_color=BG, corner_radius=0)
        stats_frame.pack(fill="x", padx=24, pady=16)
        for col, (label, val, color) in enumerate([
            ("Tổng doanh thu", f"{total_rev:,.0f} đ", ORANGE),
            ("Hội viên Active", str(active_m), EMERALD),
            ("Hội viên Expired", str(expired_m), RED),
            ("Tổng lượt tập", str(total_att), BLUE),
        ]):
            card = ctk.CTkFrame(stats_frame, fg_color=WHITE, corner_radius=16,
                                 border_width=1, border_color=BORDER)
            card.grid(row=0, column=col, padx=(0, 12) if col < 3 else (0, 0), sticky="ew")
            stats_frame.grid_columnconfigure(col, weight=1)
            ctk.CTkLabel(card, text=label,
                         font=ctk.CTkFont(size=9, weight="bold"),
                         text_color=TEXT_MUTED).pack(anchor="w", padx=16, pady=(12, 0))
            ctk.CTkLabel(card, text=val,
                         font=ctk.CTkFont(size=22, weight="bold"),
                         text_color=color).pack(anchor="w", padx=16, pady=(0, 12))

        # === Revenue by month chart ===
        if HAS_MPL:
            rev_by_month = defaultdict(float)
            for inv in invoices:
                try:
                    month = inv.date[:7]  # YYYY-MM
                    rev_by_month[month] += inv.total
                except Exception:
                    pass
            months = sorted(rev_by_month.keys())[-6:]
            values = [rev_by_month[m] for m in months]

            chart_card = ctk.CTkFrame(scroll, fg_color=WHITE, corner_radius=20,
                                       border_width=1, border_color=BORDER)
            chart_card.pack(fill="x", padx=24, pady=(0, 16))
            ctk.CTkLabel(chart_card, text="Doanh thu theo tháng (6 tháng gần nhất)",
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=TEXT_PRIMARY).pack(anchor="w", padx=24, pady=(16, 8))

            fig, ax = plt.subplots(figsize=(9, 3), dpi=96)
            fig.patch.set_facecolor("#ffffff")
            ax.set_facecolor("#ffffff")
            bars = ax.bar(months, values, color=ORANGE, alpha=0.85, width=0.5, zorder=2)
            ax.bar_label(bars, labels=[f"{v/1e6:.1f}M" if v >= 1e6 else f"{v:,.0f}" for v in values],
                         fontsize=9, color=TEXT_SECONDARY, padding=4)
            ax.set_xticks(range(len(months)))
            ax.set_xticklabels(months, fontsize=9, color="#94a3b8")
            ax.tick_params(axis="y", labelsize=9, labelcolor="#94a3b8")
            ax.grid(axis="y", color="#f1f5f9", linewidth=1, zorder=1)
            ax.spines[:].set_visible(False)
            fig.tight_layout(pad=1.2)
            canvas = FigureCanvasTkAgg(fig, master=chart_card)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="x", padx=20, pady=(0, 16))
            plt.close(fig)

        # === Member status pie ===
        row2 = ctk.CTkFrame(scroll, fg_color=BG, corner_radius=0)
        row2.pack(fill="x", padx=24, pady=(0, 24))
        row2.grid_columnconfigure((0, 1), weight=1)

        if HAS_MPL and members:
            pie_card = ctk.CTkFrame(row2, fg_color=WHITE, corner_radius=20,
                                     border_width=1, border_color=BORDER)
            pie_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
            ctk.CTkLabel(pie_card, text="Tình trạng hội viên",
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=TEXT_PRIMARY).pack(anchor="w", padx=24, pady=(16, 8))

            status_counts = defaultdict(int)
            for m in members:
                status_counts[m.status] += 1

            fig2, ax2 = plt.subplots(figsize=(3.5, 3), dpi=96)
            fig2.patch.set_facecolor("#ffffff")
            colors_pie = [EMERALD, RED, ORANGE]
            ax2.pie(status_counts.values(), labels=status_counts.keys(),
                    colors=colors_pie[:len(status_counts)],
                    autopct="%1.0f%%", startangle=90,
                    textprops={"fontsize": 10, "color": "#64748b"})
            fig2.tight_layout(pad=0.5)
            canvas2 = FigureCanvasTkAgg(fig2, master=pie_card)
            canvas2.draw()
            canvas2.get_tk_widget().pack(fill="x", padx=20, pady=(0, 16))
            plt.close(fig2)

        # Top invoices table
        top_inv_card = ctk.CTkFrame(row2, fg_color=WHITE, corner_radius=20,
                                     border_width=1, border_color=BORDER)
        top_inv_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        ctk.CTkLabel(top_inv_card, text="Hóa đơn lớn nhất",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=24, pady=(16, 8))

        members_map = {m.id: m for m in members}
        top5 = sorted(invoices, key=lambda i: i.total, reverse=True)[:8]
        for inv in top5:
            member = members_map.get(inv.memberId)
            mname = member.fullName if member else inv.memberId
            row = ctk.CTkFrame(top_inv_card, fg_color="#f8fafc", corner_radius=8)
            row.pack(fill="x", padx=12, pady=3)
            ctk.CTkLabel(row, text=mname,
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=TEXT_PRIMARY).pack(side="left", padx=12, pady=8)
            ctk.CTkLabel(row, text=f"{inv.total:,.0f} đ",
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=ORANGE).pack(side="right", padx=12, pady=8)
            ctk.CTkLabel(row, text=inv.date[:10],
                         font=ctk.CTkFont(size=9),
                         text_color=TEXT_MUTED).pack(side="right", padx=(0, 4), pady=8)
