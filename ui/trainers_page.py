"""
Huấn luyện viên — Trainers Page
"""
import customtkinter as ctk
from ui.app import (ORANGE, ORANGE_DARK, ORANGE_LIGHT, WHITE, BG,
                     TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, BORDER, EMERALD, RED, BLUE)


class TrainersPage(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, fg_color=BG, corner_radius=0, **kwargs)
        self.app = app
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", lambda *a: self._refresh())
        self._build()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        top.pack(fill="x", padx=24, pady=(20, 0))

        ctk.CTkLabel(top, text="HUẤN LUYỆN VIÊN",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(side="left")

        sf = ctk.CTkFrame(top, fg_color=WHITE, corner_radius=12,
                           border_width=1, border_color=BORDER)
        sf.pack(side="right")
        ctk.CTkLabel(sf, text="🔍").pack(side="left", padx=(12, 0))
        ctk.CTkEntry(sf, textvariable=self.search_var,
                     placeholder_text="Tìm HLV...",
                     width=200, height=38, border_width=0,
                     fg_color=WHITE, text_color=TEXT_PRIMARY,
                     font=ctk.CTkFont(size=12)).pack(side="left", padx=8)

        self.scroll = ctk.CTkScrollableFrame(self, fg_color=BG, corner_radius=0,
                                              scrollbar_button_color=BORDER)
        self.scroll.pack(fill="both", expand=True, padx=16, pady=16)
        self._refresh()

    def _refresh(self):
        for w in self.scroll.winfo_children():
            w.destroy()

        term = self.search_var.get().lower()
        trainers = [u for u in self.app.data["users"]
                    if u.role == "PT"
                    and (not term or term in u.fullName.lower())]

        if not trainers:
            ctk.CTkLabel(self.scroll, text="Không có huấn luyện viên nào",
                         font=ctk.CTkFont(size=13), text_color=TEXT_MUTED).pack(pady=60)
            return

        COLS = 3
        for i, trainer in enumerate(trainers):
            row = i // COLS
            col = i % COLS
            self.scroll.grid_columnconfigure(col, weight=1)

            # Count members assigned
            m_count = sum(1 for m in self.app.data["members"]
                          if m.assignedPTId == trainer.id)

            card = ctk.CTkFrame(self.scroll, fg_color=WHITE, corner_radius=20,
                                 border_width=1, border_color=BORDER)
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

            # Avatar
            initials = "".join(w[0] for w in trainer.fullName.split() if w)[-1:].upper()
            ctk.CTkLabel(card, text=initials,
                         font=ctk.CTkFont(size=28, weight="bold"),
                         fg_color="#dbeafe", text_color=BLUE,
                         corner_radius=14, width=64, height=64).pack(pady=(20, 0))

            ctk.CTkLabel(card, text=trainer.fullName.upper(),
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=TEXT_PRIMARY).pack(pady=(8, 0))
            ctk.CTkLabel(card, text=f"@{trainer.username}",
                         font=ctk.CTkFont(size=10, weight="bold"),
                         text_color=TEXT_MUTED).pack()

            sep = ctk.CTkFrame(card, fg_color=BORDER, height=1, corner_radius=0)
            sep.pack(fill="x", padx=20, pady=12)

            detail = ctk.CTkFrame(card, fg_color="#f8fafc", corner_radius=12,
                                   border_width=1, border_color=BORDER)
            detail.pack(fill="x", padx=16, pady=(0, 16))

            rows_data = [
                ("🎯 Chuyên môn", trainer.specialty or "Fitness tổng hợp"),
                ("👥 Học viên", f"{m_count} người"),
            ]
            for ri, (lbl, val) in enumerate(rows_data):
                detail.grid_columnconfigure(1, weight=1)
                ctk.CTkLabel(detail, text=lbl,
                             font=ctk.CTkFont(size=9, weight="bold"),
                             text_color=TEXT_MUTED).grid(row=ri, column=0, padx=12, pady=6, sticky="w")
                ctk.CTkLabel(detail, text=val,
                             font=ctk.CTkFont(size=11, weight="bold"),
                             text_color=TEXT_PRIMARY).grid(row=ri, column=1, padx=12, pady=6, sticky="e")
