"""
Quản lý Hội Viên — Members Page
Chức năng: Xem danh sách (grid card), Tìm kiếm, Thêm, Sửa, Xóa
"""
import customtkinter as ctk
import time
from models.models import Member
import services.member_service as ms
from ui.app import (ORANGE, ORANGE_DARK, ORANGE_LIGHT, WHITE, BG,
                     TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, BORDER, EMERALD, RED, BLUE)


class MembersPage(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, fg_color=BG, corner_radius=0, **kwargs)
        self.app = app
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", lambda *a: self._refresh_list())
        self._build()

    def _build(self):
        # Top bar
        top = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        top.pack(fill="x", padx=24, pady=(20, 0))
        top.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(top, text="QUẢN LÝ HỘI VIÊN",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=TEXT_PRIMARY).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(top, text="Thông tin khách hàng & Tài khoản đăng nhập",
                     font=ctk.CTkFont(size=11), text_color=TEXT_MUTED).grid(row=1, column=0, sticky="w")

        actions = ctk.CTkFrame(top, fg_color=BG, corner_radius=0)
        actions.grid(row=0, column=2, rowspan=2, sticky="e")

        # Search
        search_frame = ctk.CTkFrame(actions, fg_color=WHITE, corner_radius=12,
                                     border_width=1, border_color=BORDER)
        search_frame.pack(side="left", padx=(0, 12))
        ctk.CTkLabel(search_frame, text="🔍", font=ctk.CTkFont(size=14)).pack(side="left", padx=(12, 0))
        ctk.CTkEntry(search_frame, textvariable=self.search_var,
                     placeholder_text="Tìm tên, SĐT...",
                     width=220, height=40, border_width=0,
                     fg_color=WHITE, text_color=TEXT_PRIMARY,
                     font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=8)

        role = self.app.current_user.role
        if role in ("ADMIN", "MANAGER", "RECEPTIONIST"):
            ctk.CTkButton(actions, text="＋  Thêm mới",
                          font=ctk.CTkFont(size=11, weight="bold"),
                          fg_color=ORANGE, hover_color=ORANGE_DARK,
                          height=42, corner_radius=12,
                          command=self._open_add_dialog).pack(side="left")

        # Scrollable grid
        self.scroll = ctk.CTkScrollableFrame(self, fg_color=BG, corner_radius=0,
                                              scrollbar_button_color=BORDER)
        self.scroll.pack(fill="both", expand=True, padx=16, pady=16)

        self._refresh_list()

    def _refresh_list(self):
        for w in self.scroll.winfo_children():
            w.destroy()

        term = self.search_var.get().lower()
        members = [
            m for m in self.app.data["members"]
            if term in m.fullName.lower()
            or term in m.phone
            or term in m.id.lower()
        ]

        if not members:
            ctk.CTkLabel(self.scroll, text="Không tìm thấy hội viên nào",
                         font=ctk.CTkFont(size=13), text_color=TEXT_MUTED).pack(pady=60)
            return

        COLS = 3
        for i, member in enumerate(members):
            row = i // COLS
            col = i % COLS
            self.scroll.grid_columnconfigure(col, weight=1)
            self._member_card(self.scroll, member).grid(
                row=row, column=col, padx=8, pady=8, sticky="nsew"
            )

    def _member_card(self, parent, member: Member):
        card = ctk.CTkFrame(parent, fg_color=WHITE, corner_radius=20,
                             border_width=1, border_color=BORDER)

        # Avatar + name row
        top = ctk.CTkFrame(card, fg_color=WHITE, corner_radius=0)
        top.pack(fill="x", padx=20, pady=(20, 0))

        initials = "".join(w[0] for w in member.fullName.split() if w)[-1:].upper()
        avatar = ctk.CTkLabel(top, text=initials,
                               font=ctk.CTkFont(size=22, weight="bold"),
                               fg_color="#fed7aa", text_color=ORANGE,
                               corner_radius=12, width=56, height=56)
        avatar.pack(side="left")

        info = ctk.CTkFrame(top, fg_color=WHITE, corner_radius=0)
        info.pack(side="left", padx=(12, 0), fill="both", expand=True)
        ctk.CTkLabel(info, text=member.fullName.upper(),
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT_PRIMARY, anchor="w").pack(anchor="w")
        ctk.CTkLabel(info, text=f"@{member.username or 'chưa cấp'}",
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=TEXT_MUTED, anchor="w").pack(anchor="w")

        status_color = EMERALD if member.status == "ACTIVE" else RED
        ctk.CTkLabel(top, text="●",
                     font=ctk.CTkFont(size=14),
                     text_color=status_color).pack(side="right", padx=(0, 0))

        # Details
        detail = ctk.CTkFrame(card, fg_color="#f8fafc", corner_radius=12,
                               border_width=1, border_color=BORDER)
        detail.pack(fill="x", padx=16, pady=12)

        rows_data = [
            ("📱 Liên hệ", member.phone),
            ("📍 Quê quán", member.homeTown or "---"),
            ("⚖ Cân nặng", f"{member.weight or '--'} kg"),
            ("📋 Trạng thái", member.status),
        ]
        for r, (lbl, val) in enumerate(rows_data):
            detail.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(detail, text=lbl,
                         font=ctk.CTkFont(size=9, weight="bold"),
                         text_color=TEXT_MUTED).grid(row=r, column=0, padx=12, pady=3, sticky="w")
            text_color = (EMERALD if val == "ACTIVE" else RED) if lbl.endswith("Trạng thái") else TEXT_PRIMARY
            ctk.CTkLabel(detail, text=val,
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=text_color).grid(row=r, column=1, padx=12, pady=3, sticky="e")

        # Buttons
        btn_row = ctk.CTkFrame(card, fg_color=WHITE, corner_radius=0)
        btn_row.pack(fill="x", padx=16, pady=(0, 16))
        btn_row.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(btn_row, text="✏ Sửa",
                      fg_color="#f1f5f9", text_color=TEXT_SECONDARY,
                      hover_color="#dbeafe", font=ctk.CTkFont(size=11, weight="bold"),
                      corner_radius=10, height=36,
                      command=lambda m=member: self._open_edit_dialog(m)).grid(row=0, column=0, sticky="ew", padx=(0, 4))

        role = self.app.current_user.role
        if role not in ("PT",):
            ctk.CTkButton(btn_row, text="🗑 Xóa",
                          fg_color="#f1f5f9", text_color=TEXT_SECONDARY,
                          hover_color="#fee2e2", font=ctk.CTkFont(size=11, weight="bold"),
                          corner_radius=10, height=36,
                          command=lambda m=member: self._confirm_delete(m)).grid(row=0, column=1, sticky="ew", padx=(4, 0))
        return card

    # ------------------------------------------------------------------
    # Dialogs
    # ------------------------------------------------------------------
    def _open_add_dialog(self):
        MemberFormDialog(self, title="Đăng ký Hội Viên Mới",
                         on_save=self._save_add)

    def _open_edit_dialog(self, member):
        MemberFormDialog(self, title="Cập nhật tài khoản Hội viên",
                         member=member, on_save=self._save_edit)

    def _save_add(self, data: dict):
        new = Member(
            id=f"m{int(time.time()*1000)}",
            fullName=data["fullName"],
            phone=data["phone"],
            email=data["email"],
            homeTown=data["homeTown"],
            username=data["username"],
            password=data["password"],
            joinDate=str(__import__('datetime').date.today()),
            status="ACTIVE",
            weight=float(data["weight"] or 0),
            previousWeight=0.0
        )
        try:
            ms.add(new)
            self.app.data["members"].append(new)
            self._refresh_list()
            self.app.show_notification(f"Đã thêm hội viên {new.fullName}", "success")
        except Exception as e:
            self.app.show_notification(f"Lỗi: {e}", "error")

    def _save_edit(self, data: dict):
        member = data["__member__"]
        member.fullName = data["fullName"]
        member.phone    = data["phone"]
        member.email    = data["email"]
        member.homeTown = data["homeTown"]
        member.username = data["username"]
        if data["password"]:
            member.password = data["password"]
        try:
            w = float(data["weight"] or member.weight)
        except ValueError:
            w = member.weight
        member.weight = w
        try:
            ms.update(member)
            self._refresh_list()
            self.app.show_notification(f"Đã cập nhật {member.fullName}", "success")
        except Exception as e:
            self.app.show_notification(f"Lỗi: {e}", "error")

    def _confirm_delete(self, member):
        dlg = ctk.CTkToplevel(self)
        dlg.title("Xác nhận xóa")
        dlg.geometry("340x200")
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.configure(fg_color=WHITE)
        ctk.CTkLabel(dlg, text="🗑 Xóa Hội Viên?",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(pady=(28, 4))
        ctk.CTkLabel(dlg, text=f"Dữ liệu của {member.fullName}\nsẽ bị xóa vĩnh viễn.",
                     font=ctk.CTkFont(size=11), text_color=TEXT_SECONDARY,
                     justify="center").pack(pady=(0, 20))
        row = ctk.CTkFrame(dlg, fg_color=WHITE, corner_radius=0)
        row.pack(fill="x", padx=24)
        ctk.CTkButton(row, text="Hủy", fg_color="#f1f5f9",
                       text_color=TEXT_SECONDARY, hover_color=BORDER,
                       font=ctk.CTkFont(weight="bold"),
                       command=dlg.destroy).pack(side="left", expand=True, fill="x", padx=(0, 6))
        ctk.CTkButton(row, text="Xác nhận xóa", fg_color=RED,
                       hover_color="#dc2626", text_color=WHITE,
                       font=ctk.CTkFont(weight="bold"),
                       command=lambda: self._do_delete(member, dlg)).pack(side="left", expand=True, fill="x", padx=(6, 0))

    def _do_delete(self, member, dlg):
        dlg.destroy()
        try:
            ms.delete(member.id)
            self.app.data["members"] = [m for m in self.app.data["members"] if m.id != member.id]
            self._refresh_list()
            self.app.show_notification("Đã xóa hội viên thành công", "success")
        except Exception as e:
            self.app.show_notification(f"Lỗi: {e}", "error")


class MemberFormDialog(ctk.CTkToplevel):
    def __init__(self, master, title, on_save, member: Member = None):
        super().__init__(master)
        self.title(title)
        self.geometry("520x580")
        self.resizable(False, True)
        self.grab_set()
        self.configure(fg_color=WHITE)
        self.member = member
        self.on_save = on_save
        self._build(title)

    def _build(self, title):
        # Header
        header = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=0,
                               border_width=0, border_color=BORDER, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(header, text=title.upper(),
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(side="left", padx=24, pady=18)
        ctk.CTkButton(header, text="✕", width=36, height=36,
                       fg_color="transparent", text_color=TEXT_MUTED,
                       hover_color="#f1f5f9", font=ctk.CTkFont(size=14),
                       command=self.destroy).pack(side="right", padx=12)

        sep = ctk.CTkFrame(self, fg_color=BORDER, height=1, corner_radius=0)
        sep.pack(fill="x")

        # Scrollable body
        body = ctk.CTkScrollableFrame(self, fg_color=WHITE, corner_radius=0,
                                       scrollbar_button_color=BORDER)
        body.pack(fill="both", expand=True)

        m = self.member

        def field(label, name, default="", show=""):
            ctk.CTkLabel(body, text=label,
                         font=ctk.CTkFont(size=9, weight="bold"),
                         text_color=TEXT_MUTED, anchor="w").pack(fill="x", padx=24, pady=(12, 2))
            entry = ctk.CTkEntry(body, height=44, corner_radius=10,
                                  border_color=BORDER, border_width=1,
                                  fg_color="#f8fafc", text_color=TEXT_PRIMARY,
                                  font=ctk.CTkFont(size=13, weight="bold"),
                                  show=show)
            entry.pack(fill="x", padx=24)
            if default:
                entry.insert(0, default)
            setattr(self, f"_{name}_entry", entry)
            return entry

        field("HỌ VÀ TÊN *", "fullName", m.fullName if m else "")
        field("SỐ ĐIỆN THOẠI *", "phone", m.phone if m else "")
        field("QUÊ QUÁN", "homeTown", m.homeTown or "" if m else "")

        # Login section
        login_box = ctk.CTkFrame(body, fg_color="#fff7ed", corner_radius=14,
                                  border_width=1, border_color="#fed7aa")
        login_box.pack(fill="x", padx=24, pady=(16, 0))
        ctk.CTkLabel(login_box, text="THÔNG TIN ĐĂNG NHẬP ỨNG DỤNG",
                     font=ctk.CTkFont(size=9, weight="bold"),
                     text_color=ORANGE).pack(pady=(12, 4))

        row2 = ctk.CTkFrame(login_box, fg_color="transparent", corner_radius=0)
        row2.pack(fill="x", padx=12, pady=(0, 12))
        row2.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(row2, text="TÊN ĐĂNG NHẬP *",
                     font=ctk.CTkFont(size=9, weight="bold"),
                     text_color=TEXT_MUTED).grid(row=0, column=0, sticky="w", pady=(0, 2))
        self._username_entry = ctk.CTkEntry(row2, height=40, corner_radius=8,
                                             border_color=BORDER, border_width=1,
                                             fg_color=WHITE, text_color=TEXT_PRIMARY,
                                             font=ctk.CTkFont(size=12, weight="bold"))
        self._username_entry.grid(row=1, column=0, sticky="ew", padx=(0, 6))
        if m and m.username:
            self._username_entry.insert(0, m.username)

        ctk.CTkLabel(row2, text="MẬT KHẨU" + (" MỚI" if m else " *"),
                     font=ctk.CTkFont(size=9, weight="bold"),
                     text_color=TEXT_MUTED).grid(row=0, column=1, sticky="w", pady=(0, 2))
        self._password_entry = ctk.CTkEntry(row2, show="●", height=40, corner_radius=8,
                                             border_color=BORDER, border_width=1,
                                             fg_color=WHITE, text_color=TEXT_PRIMARY,
                                             font=ctk.CTkFont(size=12, weight="bold"),
                                             placeholder_text="••••••••")
        self._password_entry.grid(row=1, column=1, sticky="ew", padx=(6, 0))

        row3 = ctk.CTkFrame(body, fg_color="transparent", corner_radius=0)
        row3.pack(fill="x", padx=24, pady=(12, 0))
        row3.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(row3, text="EMAIL *",
                     font=ctk.CTkFont(size=9, weight="bold"),
                     text_color=TEXT_MUTED).grid(row=0, column=0, sticky="w", pady=(0, 2))
        self._email_entry = ctk.CTkEntry(row3, height=44, corner_radius=10,
                                          border_color=BORDER, border_width=1,
                                          fg_color="#f8fafc", text_color=TEXT_PRIMARY,
                                          font=ctk.CTkFont(size=13, weight="bold"))
        self._email_entry.grid(row=1, column=0, sticky="ew", padx=(0, 6))
        if m and m.email:
            self._email_entry.insert(0, m.email)

        ctk.CTkLabel(row3, text="CÂN NẶNG (kg)",
                     font=ctk.CTkFont(size=9, weight="bold"),
                     text_color=TEXT_MUTED).grid(row=0, column=1, sticky="w", pady=(0, 2))
        self._weight_entry = ctk.CTkEntry(row3, height=44, corner_radius=10,
                                           border_color=BORDER, border_width=1,
                                           fg_color="#f8fafc", text_color=TEXT_PRIMARY,
                                           font=ctk.CTkFont(size=13, weight="bold"))
        self._weight_entry.grid(row=1, column=1, sticky="ew", padx=(6, 0))
        if m and m.weight:
            self._weight_entry.insert(0, str(m.weight))

        # Footer
        sep2 = ctk.CTkFrame(self, fg_color=BORDER, height=1, corner_radius=0)
        sep2.pack(fill="x")
        foot = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=0, height=72)
        foot.pack(fill="x")
        foot.pack_propagate(False)
        foot.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(foot, text="Hủy", fg_color="#f1f5f9",
                       text_color=TEXT_SECONDARY, hover_color=BORDER,
                       font=ctk.CTkFont(weight="bold"), height=44, corner_radius=12,
                       command=self.destroy).grid(row=0, column=0, padx=(24, 6), pady=14, sticky="ew")
        btn_text = "Cập nhật thông tin" if self.member else "Kích hoạt hội viên"
        btn_color = BLUE if self.member else ORANGE
        ctk.CTkButton(foot, text=btn_text, fg_color=btn_color,
                       hover_color=ORANGE_DARK if not self.member else "#2563eb",
                       text_color=WHITE,
                       font=ctk.CTkFont(weight="bold"), height=44, corner_radius=12,
                       command=self._submit).grid(row=0, column=1, padx=(6, 24), pady=14, sticky="ew")

    def _submit(self):
        data = {
            "fullName": self._fullName_entry.get().strip(),
            "phone":    self._phone_entry.get().strip(),
            "homeTown": self._homeTown_entry.get().strip(),
            "username": self._username_entry.get().strip(),
            "password": self._password_entry.get().strip(),
            "email":    self._email_entry.get().strip(),
            "weight":   self._weight_entry.get().strip(),
        }
        if not data["fullName"] or not data["phone"] or not data["username"]:
            return
        if self.member:
            data["__member__"] = self.member
        self.destroy()
        self.on_save(data)
