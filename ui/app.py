"""
Main Application Window — GymThep Pro System
Layout: Sidebar (trái) + Content area (phải)
"""
import customtkinter as ctk
from datetime import datetime
from typing import Optional

# Color palette
ORANGE = "#f97316"
ORANGE_DARK = "#ea6c0a"
ORANGE_LIGHT = "#fff7ed"
BG = "#f8fafc"
WHITE = "#ffffff"
SIDEBAR_BG = "#ffffff"
TEXT_PRIMARY = "#0f172a"
TEXT_SECONDARY = "#64748b"
TEXT_MUTED = "#94a3b8"
BORDER = "#e2e8f0"
EMERALD = "#10b981"
RED = "#ef4444"
BLUE = "#3b82f6"
SLATE_900 = "#0f172a"

# Role → accessible pages
ROLE_MENU = {
    "ADMIN":        ["dashboard", "events", "members", "classes", "billing", "inventory", "trainers", "reports", "system_users"],
    "MANAGER":      ["dashboard", "events", "members", "classes", "billing", "inventory", "trainers", "reports"],
    "RECEPTIONIST": ["events", "members", "classes", "billing", "trainers"],
    "PT":           ["members", "classes"],
    "MEMBER":       ["profile", "classes"],
}

MENU_LABELS = {
    "dashboard":    "Tổng quan",
    "events":       "Sự Kiện",
    "members":      "Hội viên",
    "trainers":     "Huấn luyện viên",
    "classes":      "Lớp học",
    "billing":      "Tài chính",
    "inventory":    "Kho & Thiết bị",
    "reports":      "Báo cáo",
    "system_users": "Hệ thống",
    "profile":      "Cá nhân",
}

MENU_ICONS = {
    "dashboard":    "📊",
    "events":       "🎉",
    "members":      "👥",
    "trainers":     "🏅",
    "classes":      "⚽",
    "billing":      "💳",
    "inventory":    "📦",
    "reports":      "📈",
    "system_users": "🛡️",
    "profile":      "👤",
}


class SportsClubApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.title("CLB Thể Thao — Pro System")
        self.geometry("1366x768")
        self.minsize(1024, 640)
        self.configure(fg_color=BG)

        # State
        self.current_user = None
        self.current_page_key: Optional[str] = None
        self._page_cache: dict = {}

        # Data store (loaded once, shared across pages)
        self.data = {
            "members": [],
            "plans": [],
            "products": [],
            "classes": [],
            "invoices": [],
            "events": [],
            "users": [],
        }

        self._build_layout()
        self._show_login()

    # ------------------------------------------------------------------
    # Layout builders
    # ------------------------------------------------------------------
    def _build_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=260, fg_color=SIDEBAR_BG,
                                    corner_radius=0, border_width=1,
                                    border_color=BORDER)
        self.sidebar.grid(row=0, column=0, sticky="nsw")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(2, weight=1)

        self._build_sidebar_logo()
        self._build_sidebar_nav()
        self._build_sidebar_user()

        # Main content
        self.content_wrapper = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        self.content_wrapper.grid(row=0, column=1, sticky="nsew")
        self.content_wrapper.grid_rowconfigure(1, weight=1)
        self.content_wrapper.grid_columnconfigure(0, weight=1)

        self._build_topbar()

        self.content_frame = ctk.CTkFrame(self.content_wrapper, fg_color=BG, corner_radius=0)
        self.content_frame.grid(row=1, column=0, sticky="nsew")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # Notification overlay
        self._notif_labels = []

        # Initially hide sidebar until login
        self.sidebar.grid_remove()
        self.content_wrapper.grid_remove()

        # Login frame overlay
        self.login_frame = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        self.login_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")

    def _build_sidebar_logo(self):
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color=SIDEBAR_BG,
                                   height=72, corner_radius=0)
        logo_frame.grid(row=0, column=0, sticky="ew", padx=0)
        logo_frame.grid_propagate(False)
        logo_frame.grid_columnconfigure(0, weight=1)

        inner = ctk.CTkFrame(logo_frame, fg_color=SIDEBAR_BG, corner_radius=0)
        inner.pack(fill="both", expand=True, padx=20)

        icon_box = ctk.CTkLabel(inner, text="🏆", font=ctk.CTkFont(size=24),
                                 fg_color=ORANGE, corner_radius=10,
                                 width=40, height=40)
        icon_box.pack(side="left", pady=16)

        text_frame = ctk.CTkFrame(inner, fg_color=SIDEBAR_BG, corner_radius=0)
        text_frame.pack(side="left", padx=(10, 0), pady=16)
        ctk.CTkLabel(text_frame, text="CLB Thể Thao",
                     font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(text_frame, text="PRO SYSTEM",
                     font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
                     text_color=ORANGE).pack(anchor="w")

    def _build_sidebar_nav(self):
        self.nav_frame = ctk.CTkScrollableFrame(self.sidebar, fg_color=SIDEBAR_BG,
                                                 corner_radius=0, scrollbar_button_color=BORDER)
        self.nav_frame.grid(row=2, column=0, sticky="nsew", padx=8, pady=8)
        self.nav_buttons: dict = {}

    def _build_sidebar_user(self):
        self.user_panel = ctk.CTkFrame(self.sidebar, fg_color=SIDEBAR_BG,
                                        corner_radius=0, border_width=1,
                                        border_color=BORDER, height=100)
        self.user_panel.grid(row=3, column=0, sticky="sew", padx=0)
        self.user_panel.grid_propagate(False)
        self.user_panel.grid_columnconfigure(0, weight=1)

        self.user_avatar_lbl = ctk.CTkLabel(self.user_panel, text="?",
                                              font=ctk.CTkFont(size=16, weight="bold"),
                                              fg_color="#fed7aa", text_color=ORANGE,
                                              corner_radius=10, width=40, height=40)
        self.user_avatar_lbl.grid(row=0, column=0, sticky="w", padx=16, pady=(14, 0))

        self.user_name_lbl = ctk.CTkLabel(self.user_panel, text="",
                                            font=ctk.CTkFont(size=13, weight="bold"),
                                            text_color=TEXT_PRIMARY)
        self.user_name_lbl.grid(row=0, column=1, sticky="w", padx=(0, 16))

        self.user_role_lbl = ctk.CTkLabel(self.user_panel, text="",
                                           font=ctk.CTkFont(size=10, weight="bold"),
                                           text_color=ORANGE)
        self.user_role_lbl.grid(row=1, column=1, sticky="w", padx=(0, 16))

        logout_btn = ctk.CTkButton(self.user_panel, text="⟵  Đăng xuất",
                                    font=ctk.CTkFont(size=11, weight="bold"),
                                    fg_color="transparent", text_color=TEXT_MUTED,
                                    hover_color="#fef2f2",
                                    command=self._confirm_logout, anchor="w",
                                    height=32, corner_radius=8)
        logout_btn.grid(row=2, column=0, columnspan=2, sticky="ew",
                        padx=12, pady=(4, 12))

    def _build_topbar(self):
        self.topbar = ctk.CTkFrame(self.content_wrapper, fg_color=WHITE,
                                    corner_radius=0, height=60,
                                    border_width=1, border_color=BORDER)
        self.topbar.grid(row=0, column=0, sticky="ew")
        self.topbar.grid_propagate(False)
        self.topbar.grid_columnconfigure(1, weight=1)

        self.page_title_lbl = ctk.CTkLabel(self.topbar, text="",
                                            font=ctk.CTkFont(size=16, weight="bold"),
                                            text_color=TEXT_PRIMARY)
        self.page_title_lbl.grid(row=0, column=0, padx=24, pady=0, sticky="w")

        date_str = datetime.now().strftime("%a, %d/%m/%Y")
        date_frame = ctk.CTkFrame(self.topbar, fg_color=WHITE, corner_radius=20,
                                   border_width=1, border_color=BORDER)
        date_frame.grid(row=0, column=2, padx=16, pady=10, sticky="e")
        ctk.CTkLabel(date_frame, text=f"● {date_str}",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=TEXT_SECONDARY).pack(padx=16, pady=4)

    # ------------------------------------------------------------------
    # Login flow
    # ------------------------------------------------------------------
    def _show_login(self):
        from ui.login_page import LoginPage
        for w in self.login_frame.winfo_children():
            w.destroy()
        LoginPage(self.login_frame, on_login_success=self._on_login).pack(fill="both", expand=True)
        self.login_frame.grid()
        self.sidebar.grid_remove()
        self.content_wrapper.grid_remove()

    def _on_login(self, user):
        self.current_user = user
        self.login_frame.grid_remove()

        # Update user panel
        initials = "".join(w[0] for w in user.fullName.split() if w)[:2].upper()
        self.user_avatar_lbl.configure(text=initials)
        self.user_name_lbl.configure(text=user.fullName)
        self.user_role_lbl.configure(text=user.role)

        # Build nav
        self._populate_nav()

        # Show layout
        self.sidebar.grid()
        self.content_wrapper.grid()
        self.sidebar.grid_columnconfigure(0, weight=1)

        # Load data then go to first page
        self._load_data()
        pages = ROLE_MENU.get(user.role, [])
        if pages:
            self.navigate(pages[0])

    def _populate_nav(self):
        for w in self.nav_frame.winfo_children():
            w.destroy()
        self.nav_buttons.clear()
        pages = ROLE_MENU.get(self.current_user.role, [])
        for key in pages:
            icon = MENU_ICONS.get(key, "•")
            label = MENU_LABELS.get(key, key)
            btn = ctk.CTkButton(
                self.nav_frame,
                text=f"  {icon}  {label}",
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                fg_color="transparent", text_color=TEXT_SECONDARY,
                hover_color=ORANGE_LIGHT, anchor="w",
                corner_radius=12, height=44,
                command=lambda k=key: self.navigate(k)
            )
            btn.pack(fill="x", pady=2)
            self.nav_buttons[key] = btn

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------
    def navigate(self, page_key: str):
        if self.current_page_key == page_key:
            return
        self.current_page_key = page_key

        # Update nav highlight
        for k, btn in self.nav_buttons.items():
            if k == page_key:
                btn.configure(fg_color=ORANGE, text_color=WHITE,
                               hover_color=ORANGE_DARK)
            else:
                btn.configure(fg_color="transparent", text_color=TEXT_SECONDARY,
                               hover_color=ORANGE_LIGHT)

        # Update topbar title
        self.page_title_lbl.configure(text=MENU_LABELS.get(page_key, ""))

        # Clear old page
        for w in self.content_frame.winfo_children():
            w.destroy()
        self._page_cache.clear()

        # Build new page
        page_cls = self._get_page_class(page_key)
        if page_cls:
            page = page_cls(self.content_frame, app=self)
            page.pack(fill="both", expand=True)

    def _get_page_class(self, key: str):
        mapping = {
            "dashboard":    ("ui.dashboard_page",       "DashboardPage"),
            "members":      ("ui.members_page",          "MembersPage"),
            "events":       ("ui.events_page",           "EventsPage"),
            "classes":      ("ui.classes_page",          "ClassesPage"),
            "billing":      ("ui.billing_page",          "BillingPage"),
            "inventory":    ("ui.inventory_page",        "InventoryPage"),
            "trainers":     ("ui.trainers_page",         "TrainersPage"),
            "reports":      ("ui.reports_page",          "ReportsPage"),
            "system_users": ("ui.user_management_page",  "UserManagementPage"),
            "profile":      ("ui.profile_page",          "ProfilePage"),
        }
        if key not in mapping:
            return None
        mod_name, cls_name = mapping[key]
        import importlib
        mod = importlib.import_module(mod_name)
        return getattr(mod, cls_name)

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------
    def _load_data(self):
        try:
            import services.member_service as ms
            import services.plan_service as ps
            import services.product_service as prs
            import services.class_service as cs
            import services.invoice_service as ivs
            import services.user_service as us
            import services.event_service as evs

            self.data["members"]    = ms.get_all()
            self.data["plans"]      = ps.get_all()
            self.data["products"]   = prs.get_all()
            self.data["classes"]    = cs.get_all()
            self.data["invoices"]   = ivs.get_all()
            self.data["users"]      = us.get_all()
            self.data["events"]     = evs.get_all_events()
        except Exception as e:
            self.show_notification(f"Lỗi tải dữ liệu: {e}", "error")

    def refresh_data(self):
        self._load_data()
        if self.current_page_key:
            self.navigate(self.current_page_key)
            # Force re-navigate
            key = self.current_page_key
            self.current_page_key = None
            self.navigate(key)

    # ------------------------------------------------------------------
    # Notifications
    # ------------------------------------------------------------------
    def show_notification(self, message: str, ntype: str = "info"):
        colors = {
            "success": ("#ecfdf5", EMERALD),
            "error":   ("#fef2f2", RED),
            "info":    ("#eff6ff", BLUE),
        }
        bg, accent = colors.get(ntype, colors["info"])
        icons = {"success": "✓", "error": "✕", "info": "ℹ"}
        icon = icons.get(ntype, "ℹ")

        notif = ctk.CTkFrame(self, fg_color=bg, corner_radius=12,
                              border_width=2, border_color=accent)
        notif.place(relx=1.0, rely=0.0, anchor="ne",
                    x=-20, y=20 + len(self._notif_labels) * 70)
        ctk.CTkLabel(notif, text=f"{icon}  {message}",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=accent).pack(padx=16, pady=10)

        self._notif_labels.append(notif)
        self.after(3000, lambda: self._remove_notification(notif))

    def _remove_notification(self, notif):
        try:
            notif.place_forget()
            notif.destroy()
            if notif in self._notif_labels:
                self._notif_labels.remove(notif)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Logout
    # ------------------------------------------------------------------
    def _confirm_logout(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Đăng xuất")
        dialog.geometry("360x220")
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
                       command=lambda: [dialog.destroy(), self._do_logout()]).pack(side="left", expand=True, fill="x", padx=(6, 0))

    def _do_logout(self):
        self.current_user = None
        self.current_page_key = None
        self._page_cache.clear()
        self.data = {k: [] for k in self.data}
        self._show_login()
