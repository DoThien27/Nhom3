"""
Quản lý Tài khoản Hệ thống — User Management Page (ADMIN only)
"""
import customtkinter as ctk
import time
from models.models import User
import services.user_service as us
from ui.app import (ORANGE, ORANGE_DARK, ORANGE_LIGHT, WHITE, BG,
                     TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, BORDER, EMERALD, RED, BLUE)

ROLES = ["ADMIN", "MANAGER", "RECEPTIONIST", "PT"]
ROLE_COLORS = {
    "ADMIN": "#7c3aed",
    "MANAGER": BLUE,
    "RECEPTIONIST": EMERALD,
    "PT": ORANGE,
    "MEMBER": "#64748b",
}


class UserManagementPage(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, fg_color=BG, corner_radius=0, **kwargs)
        self.app = app
        self._build()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        top.pack(fill="x", padx=24, pady=(20, 0))

        ctk.CTkLabel(top, text="QUẢN LÝ HỆ THỐNG",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(side="left")

        ctk.CTkButton(top, text="＋  Thêm nhân sự",
                      font=ctk.CTkFont(size=11, weight="bold"),
                      fg_color=ORANGE, hover_color=ORANGE_DARK,
                      height=40, corner_radius=12,
                      command=self._open_add_dialog).pack(side="right")

        # Table
        table_card = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=20,
                                   border_width=1, border_color=BORDER)
        table_card.pack(fill="both", expand=True, padx=24, pady=16)
        table_card.grid_rowconfigure(1, weight=1)
        table_card.grid_columnconfigure(0, weight=1)

        cols = ["Họ tên", "Username", "Vai trò", "Chuyên môn", ""]
        widths = [200, 150, 130, 200, 160]
        hdr = ctk.CTkFrame(table_card, fg_color="#f8fafc", corner_radius=0)
        hdr.grid(row=0, column=0, sticky="ew")
        for ci, (col, w) in enumerate(zip(cols, widths)):
            ctk.CTkLabel(hdr, text=col.upper(),
                         font=ctk.CTkFont(size=8, weight="bold"),
                         text_color=TEXT_MUTED, width=w, anchor="w").grid(
                row=0, column=ci, padx=(16 if ci == 0 else 8, 0), pady=10, sticky="w")

        self.scroll = ctk.CTkScrollableFrame(table_card, fg_color=WHITE,
                                              corner_radius=0, scrollbar_button_color=BORDER)
        self.scroll.grid(row=1, column=0, sticky="nsew")

        self._refresh_table()

    def _refresh_table(self):
        for w in self.scroll.winfo_children():
            w.destroy()

        for user in self.app.data["users"]:
            role_color = ROLE_COLORS.get(user.role, TEXT_MUTED)
            row = ctk.CTkFrame(self.scroll, fg_color=WHITE, corner_radius=0)
            row.pack(fill="x")
            sep = ctk.CTkFrame(self.scroll, fg_color=BORDER, height=1, corner_radius=0)
            sep.pack(fill="x")

            widths = [200, 150, 130, 200]
            vals = [user.fullName, user.username, user.role, user.specialty or "---"]
            txt_colors = [TEXT_PRIMARY, TEXT_SECONDARY, role_color, TEXT_SECONDARY]
            for ci, (val, w, color) in enumerate(zip(vals, widths, txt_colors)):
                ctk.CTkLabel(row, text=val,
                             font=ctk.CTkFont(size=11, weight="bold" if ci == 0 else "normal"),
                             text_color=color, width=w, anchor="w").grid(
                    row=0, column=ci, padx=(16 if ci == 0 else 8, 0), pady=10, sticky="w")

            btn_frame = ctk.CTkFrame(row, fg_color=WHITE, corner_radius=0)
            btn_frame.grid(row=0, column=4, padx=8, sticky="e")
            ctk.CTkButton(btn_frame, text="✏",
                          fg_color="#f1f5f9", text_color=TEXT_SECONDARY,
                          hover_color="#dbeafe", width=32, height=32, corner_radius=8,
                          command=lambda u=user: self._open_edit_dialog(u)).pack(side="left", padx=2)
            # Protect current user from self-delete
            if user.id != self.app.current_user.id:
                ctk.CTkButton(btn_frame, text="🗑",
                              fg_color="#f1f5f9", text_color=TEXT_SECONDARY,
                              hover_color="#fee2e2", width=32, height=32, corner_radius=8,
                              command=lambda u=user: self._confirm_delete(u)).pack(side="left", padx=2)

    def _open_add_dialog(self):
        UserFormDialog(self, on_save=self._save_add)

    def _open_edit_dialog(self, user):
        UserFormDialog(self, user=user, on_save=self._save_edit)

    def _save_add(self, data):
        new_user = User(
            id=str(int(time.time() * 1000)),
            username=data["username"],
            password=data["password"],
            fullName=data["fullName"],
            role=data["role"],
            specialty=data["specialty"]
        )
        try:
            us.add(new_user)
            self.app.data["users"].append(new_user)
            self._refresh_table()
            self.app.show_notification(f"Đã thêm: {new_user.fullName}", "success")
        except Exception as e:
            self.app.show_notification(f"Lỗi: {e}", "error")

    def _save_edit(self, data):
        user = data["__user__"]
        user.fullName = data["fullName"]
        user.username = data["username"]
        user.role = data["role"]
        user.specialty = data["specialty"]
        if data["password"]:
            user.password = data["password"]
        try:
            us.update(user)
            self._refresh_table()
            self.app.show_notification(f"Đã cập nhật: {user.fullName}", "success")
        except Exception as e:
            self.app.show_notification(f"Lỗi: {e}", "error")

    def _confirm_delete(self, user):
        dlg = ctk.CTkToplevel(self)
        dlg.title("Xóa nhân sự")
        dlg.geometry("320x180")
        dlg.grab_set()
        dlg.configure(fg_color=WHITE)
        ctk.CTkLabel(dlg, text=f"Xóa '{user.fullName}'?",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(28, 8))
        row = ctk.CTkFrame(dlg, fg_color=WHITE)
        row.pack(fill="x", padx=24, pady=16)
        ctk.CTkButton(row, text="Hủy", fg_color="#f1f5f9",
                       text_color=TEXT_SECONDARY,
                       command=dlg.destroy).pack(side="left", expand=True, fill="x", padx=(0, 6))
        ctk.CTkButton(row, text="Xóa", fg_color=RED, text_color=WHITE,
                       command=lambda: [dlg.destroy(), self._do_delete(user)]).pack(side="left", expand=True, fill="x", padx=(6, 0))

    def _do_delete(self, user):
        try:
            us.delete(user.id)
            self.app.data["users"] = [u for u in self.app.data["users"] if u.id != user.id]
            self._refresh_table()
            self.app.show_notification("Đã xóa nhân sự", "success")
        except Exception as e:
            self.app.show_notification(f"Lỗi: {e}", "error")


class UserFormDialog(ctk.CTkToplevel):
    def __init__(self, master, on_save, user: User = None):
        super().__init__(master)
        self.title("Nhân sự")
        self.geometry("440x420")
        self.resizable(False, False)
        self.grab_set()
        self.configure(fg_color=WHITE)
        self.user = user
        self.on_save = on_save
        self._build()

    def _build(self):
        u = self.user
        title = "Cập nhật nhân sự" if u else "Thêm nhân sự mới"
        ctk.CTkLabel(self, text=title.upper(),
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=24, pady=(24, 12))

        def field(label, default="", show=""):
            ctk.CTkLabel(self, text=label,
                         font=ctk.CTkFont(size=9, weight="bold"),
                         text_color=TEXT_MUTED).pack(anchor="w", padx=24, pady=(8, 2))
            entry = ctk.CTkEntry(self, height=44, corner_radius=10,
                                  border_color=BORDER, border_width=1,
                                  fg_color="#f8fafc", text_color=TEXT_PRIMARY,
                                  font=ctk.CTkFont(size=13, weight="bold"), show=show)
            entry.pack(fill="x", padx=24)
            if default:
                entry.insert(0, str(default))
            return entry

        self._fullName = field("HỌ VÀ TÊN *", u.fullName if u else "")
        self._username = field("TÊN ĐĂNG NHẬP *", u.username if u else "")
        self._password = field("MẬT KHẨU" + (" MỚI" if u else " *"), show="●")
        self._specialty = field("CHUYÊN MÔN", u.specialty or "" if u else "")

        ctk.CTkLabel(self, text="VAI TRÒ *",
                     font=ctk.CTkFont(size=9, weight="bold"),
                     text_color=TEXT_MUTED).pack(anchor="w", padx=24, pady=(8, 2))
        self._role_var = ctk.StringVar(value=u.role if u else "PT")
        rf = ctk.CTkFrame(self, fg_color="#f1f5f9", corner_radius=10)
        rf.pack(fill="x", padx=24)
        for role in ROLES:
            ctk.CTkRadioButton(rf, text=role, variable=self._role_var, value=role,
                                fg_color=ORANGE, font=ctk.CTkFont(size=11, weight="bold"),
                                text_color=TEXT_PRIMARY).pack(side="left", padx=10, pady=8)

        sep = ctk.CTkFrame(self, fg_color=BORDER, height=1, corner_radius=0)
        sep.pack(fill="x", pady=(16, 0))
        foot = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=0, height=70)
        foot.pack(fill="x")
        foot.pack_propagate(False)
        foot.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(foot, text="Hủy", fg_color="#f1f5f9",
                       text_color=TEXT_SECONDARY, height=44, corner_radius=12,
                       command=self.destroy).grid(row=0, column=0, padx=(24, 6), pady=13, sticky="ew")
        ctk.CTkButton(foot, text="Lưu", fg_color=ORANGE, hover_color=ORANGE_DARK,
                       text_color=WHITE, height=44, corner_radius=12,
                       command=self._submit).grid(row=0, column=1, padx=(6, 24), pady=13, sticky="ew")

    def _submit(self):
        data = {
            "fullName": self._fullName.get().strip(),
            "username": self._username.get().strip(),
            "password": self._password.get().strip(),
            "specialty": self._specialty.get().strip(),
            "role": self._role_var.get(),
        }
        if not data["fullName"] or not data["username"]:
            return
        if self.user:
            data["__user__"] = self.user
        self.destroy()
        self.on_save(data)
