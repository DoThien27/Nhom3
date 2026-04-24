"""
Cá nhân — Profile Page (dành cho MEMBER role)
"""
import customtkinter as ctk
from ui.app import (ORANGE, ORANGE_LIGHT, WHITE, BG, TEXT_PRIMARY,
                     TEXT_SECONDARY, TEXT_MUTED, BORDER, EMERALD, RED, BLUE)


class ProfilePage(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, fg_color=BG, corner_radius=0, **kwargs)
        self.app = app
        self._build()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color=BG, corner_radius=0,
                                         scrollbar_button_color=BORDER)
        scroll.pack(fill="both", expand=True, padx=24, pady=20)

        user = self.app.current_user
        member = next((m for m in self.app.data["members"]
                       if m.username == user.username), None)

        # Profile card
        card = ctk.CTkFrame(scroll, fg_color=WHITE, corner_radius=24,
                             border_width=1, border_color=BORDER)
        card.pack(fill="x", pady=(0, 16))

        # Avatar area (gradient header)
        header = ctk.CTkFrame(card, fg_color=ORANGE, corner_radius=0, height=120)
        header.pack(fill="x")
        header.grid_propagate(False)

        initials = "".join(w[0] for w in user.fullName.split() if w)[-2:].upper()
        avatar = ctk.CTkLabel(header, text=initials,
                               font=ctk.CTkFont(size=32, weight="bold"),
                               fg_color=WHITE, text_color=ORANGE,
                               corner_radius=20, width=80, height=80)
        avatar.place(relx=0.5, rely=0.5, anchor="center")

        # Info section
        info = ctk.CTkFrame(card, fg_color=WHITE, corner_radius=0)
        info.pack(fill="x", padx=32, pady=24)

        ctk.CTkLabel(info, text=user.fullName.upper(),
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=TEXT_PRIMARY).pack()
        ctk.CTkLabel(info, text="HỘI VIÊN",
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=ORANGE).pack()

        sep = ctk.CTkFrame(card, fg_color=BORDER, height=1, corner_radius=0)
        sep.pack(fill="x", padx=32)

        # Member details
        if member:
            fields_data = [
                ("📱 Số điện thoại", member.phone),
                ("📧 Email", member.email),
                ("📍 Quê quán", member.homeTown or "---"),
                ("📅 Ngày tham gia", member.joinDate),
                ("📋 Trạng thái", member.status),
                ("🏋️ Gói tập", member.activePlanName or "---"),
                ("⏰ Hạn sử dụng", member.expiryDate or "---"),
                ("⚖ Cân nặng hiện tại", f"{member.weight or '--'} kg"),
                ("📊 Cân nặng trước", f"{member.previousWeight or '--'} kg"),
            ]
            detail_grid = ctk.CTkFrame(card, fg_color=WHITE, corner_radius=0)
            detail_grid.pack(fill="x", padx=32, pady=24)
            detail_grid.grid_columnconfigure(1, weight=1)

            for ri, (label, val) in enumerate(fields_data):
                row = ctk.CTkFrame(detail_grid, fg_color="#f8fafc" if ri % 2 == 0 else WHITE,
                                   corner_radius=8)
                row.pack(fill="x", pady=2)
                ctk.CTkLabel(row, text=label,
                             font=ctk.CTkFont(size=11, weight="bold"),
                             text_color=TEXT_MUTED, width=180, anchor="w").pack(side="left", padx=16, pady=10)
                color = EMERALD if val == "ACTIVE" else (RED if val == "EXPIRED" else TEXT_PRIMARY)
                ctk.CTkLabel(row, text=val,
                             font=ctk.CTkFont(size=11, weight="bold"),
                             text_color=color).pack(side="right", padx=16, pady=10)

            # Weight trend
            if member.weight and member.previousWeight:
                diff = member.weight - member.previousWeight
                trend_card = ctk.CTkFrame(scroll, fg_color=WHITE, corner_radius=20,
                                           border_width=1, border_color=BORDER)
                trend_card.pack(fill="x", pady=(0, 16))
                ctk.CTkLabel(trend_card, text="⚖ Thay đổi cân nặng",
                             font=ctk.CTkFont(size=13, weight="bold"),
                             text_color=TEXT_PRIMARY).pack(anchor="w", padx=24, pady=(16, 8))
                trend_frame = ctk.CTkFrame(trend_card, fg_color=BG, corner_radius=12)
                trend_frame.pack(fill="x", padx=24, pady=(0, 16))
                for col, (lbl, val, color) in enumerate([
                    ("Trước", f"{member.previousWeight} kg", TEXT_MUTED),
                    ("Hiện tại", f"{member.weight} kg", ORANGE),
                    ("Thay đổi", f"{diff:+.1f} kg", EMERALD if diff < 0 else RED),
                ]):
                    ctk.CTkLabel(trend_frame, text=lbl,
                                 font=ctk.CTkFont(size=9, weight="bold"),
                                 text_color=TEXT_MUTED).grid(row=0, column=col, padx=24, pady=(12, 0), sticky="w")
                    ctk.CTkLabel(trend_frame, text=val,
                                 font=ctk.CTkFont(size=18, weight="bold"),
                                 text_color=color).grid(row=1, column=col, padx=24, pady=(0, 12), sticky="w")
                trend_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Attendance history
        att_card = ctk.CTkFrame(scroll, fg_color=WHITE, corner_radius=20,
                                 border_width=1, border_color=BORDER)
        att_card.pack(fill="x", pady=(0, 24))
        ctk.CTkLabel(att_card, text="📋 Lịch sử tập luyện (10 gần nhất)",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=24, pady=(16, 8))

        if member:
            history = [a for a in self.app.data["attendance"] if a.memberId == member.id]
            history = sorted(history, key=lambda a: (a.date, a.time), reverse=True)[:10]
            for a in history:
                row = ctk.CTkFrame(att_card, fg_color="#f8fafc", corner_radius=8)
                row.pack(fill="x", padx=16, pady=3)
                ctk.CTkLabel(row, text=f"📅 {a.date}",
                             font=ctk.CTkFont(size=11, weight="bold"),
                             text_color=TEXT_PRIMARY).pack(side="left", padx=12, pady=8)
                ctk.CTkLabel(row, text=a.type,
                             font=ctk.CTkFont(size=10, weight="bold"),
                             text_color=ORANGE).pack(side="left", padx=4)
                ctk.CTkLabel(row, text=f"{a.time} → {a.checkOutTime or '---'}",
                             font=ctk.CTkFont(size=10),
                             text_color=TEXT_SECONDARY).pack(side="right", padx=12, pady=8)
            if not history:
                ctk.CTkLabel(att_card, text="Chưa có lịch sử tập luyện",
                             font=ctk.CTkFont(size=12), text_color=TEXT_MUTED).pack(pady=24)
        att_card.pack(pady=(0, 8))
