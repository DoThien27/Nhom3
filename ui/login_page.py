"""
Trang Đăng nhập — GymThep Pro System
"""
import customtkinter as ctk
from database.db_connection import test_connection
import services.user_service as us

ORANGE = "#f97316"
ORANGE_DARK = "#ea6c0a"
WHITE = "#ffffff"
BG = "#f8fafc"
TEXT_PRIMARY = "#0f172a"
TEXT_SECONDARY = "#64748b"
TEXT_MUTED = "#94a3b8"
BORDER = "#e2e8f0"
SLATE_50 = "#f8fafc"
RED = "#ef4444"
EMERALD = "#10b981"


class LoginPage(ctk.CTkFrame):
    def __init__(self, master, on_login_success, **kwargs):
        super().__init__(master, fg_color=SLATE_50, corner_radius=0, **kwargs)
        self.on_login_success = on_login_success
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Center card
        card = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=24,
                             border_width=1, border_color=BORDER,
                             width=420)
        card.grid(row=0, column=0)
        card.grid_propagate(False)
        card.configure(width=420)

        # Logo
        logo_frame = ctk.CTkFrame(card, fg_color="#fff7ed", corner_radius=20,
                                   width=80, height=80)
        logo_frame.pack(pady=(44, 0))
        logo_frame.pack_propagate(False)
        ctk.CTkLabel(logo_frame, text="🏆",
                     font=ctk.CTkFont(size=36)).pack(expand=True)

        ctk.CTkLabel(card, text="CLB Thể Thao",
                     font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(pady=(16, 0))
        ctk.CTkLabel(card, text="HỆ THỐNG QUẢN LÝ CÂU LẠC BỘ THỂ THAO",
                     font=ctk.CTkFont(size=9, weight="bold"),
                     text_color=ORANGE).pack()

        # Connection status
        self.conn_lbl = ctk.CTkLabel(card, text="● Đang kết nối...",
                                      font=ctk.CTkFont(size=10, weight="bold"),
                                      text_color=TEXT_MUTED)
        self.conn_lbl.pack(pady=(8, 0))

        # Form
        form = ctk.CTkFrame(card, fg_color=WHITE, corner_radius=0)
        form.pack(fill="x", padx=40, pady=24)

        ctk.CTkLabel(form, text="Tên đăng nhập",
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=TEXT_MUTED, anchor="w").pack(fill="x", pady=(0, 4))
        self.username_entry = ctk.CTkEntry(
            form, placeholder_text="Nhập username...",
            height=46, corner_radius=12, border_color=BORDER,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=SLATE_50, text_color=TEXT_PRIMARY,
            border_width=1
        )
        self.username_entry.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(form, text="Mật khẩu",
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=TEXT_MUTED, anchor="w").pack(fill="x", pady=(0, 4))
        self.password_entry = ctk.CTkEntry(
            form, placeholder_text="Nhập mật khẩu...",
            show="●", height=46, corner_radius=12, border_color=BORDER,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=SLATE_50, text_color=TEXT_PRIMARY,
            border_width=1
        )
        self.password_entry.pack(fill="x", pady=(0, 4))

        self.error_lbl = ctk.CTkLabel(form, text="",
                                       font=ctk.CTkFont(size=11),
                                       text_color=RED)
        self.error_lbl.pack(fill="x", pady=(4, 0))

        self.login_btn = ctk.CTkButton(
            form, text="ĐĂNG NHẬP",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=48, corner_radius=12,
            fg_color=ORANGE, hover_color=ORANGE_DARK,
            text_color=WHITE,
            command=self._do_login
        )
        self.login_btn.pack(fill="x", pady=(16, 0))

        # Footer
        ctk.CTkLabel(card, text="© 2025 Sports Club Pro System",
                     font=ctk.CTkFont(size=10), text_color=TEXT_MUTED).pack(pady=(0, 32))

        # Bind Enter key
        self.password_entry.bind("<Return>", lambda e: self._do_login())
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())

        # Check connection
        self.after(200, self._check_connection)

    def _check_connection(self):
        ok = test_connection()
        if ok:
            self.conn_lbl.configure(text="● Đã kết nối SQL Server", text_color=EMERALD)
        else:
            self.conn_lbl.configure(text="● Không thể kết nối SQL Server", text_color=RED)

    def _do_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            self.error_lbl.configure(text="Vui lòng nhập đầy đủ thông tin")
            return

        self.login_btn.configure(state="disabled", text="Đang đăng nhập...")
        self.error_lbl.configure(text="")
        self.after(100, lambda: self._attempt_login(username, password))

    def _attempt_login(self, username, password):
        try:
            user = us.login(username, password)
            if user:
                self.on_login_success(user)
            else:
                self.error_lbl.configure(text="Sai tên đăng nhập hoặc mật khẩu")
                self.login_btn.configure(state="normal", text="ĐĂNG NHẬP")
        except Exception as e:
            self.error_lbl.configure(text=f"Lỗi kết nối: {e}")
            self.login_btn.configure(state="normal", text="ĐĂNG NHẬP")
