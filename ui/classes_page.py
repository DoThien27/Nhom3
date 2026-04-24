"""
Lớp học — Classes Page
"""
import customtkinter as ctk
import time
from models.models import ClassSession
import services.class_service as cs
from ui.app import (ORANGE, ORANGE_DARK, ORANGE_LIGHT, WHITE, BG,
                     TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, BORDER, EMERALD, RED, BLUE)

DAYS_VI = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "CN"]


class ClassesPage(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, fg_color=BG, corner_radius=0, **kwargs)
        self.app = app
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", lambda *a: self._refresh())
        self._build()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        top.pack(fill="x", padx=24, pady=(20, 0))

        ctk.CTkLabel(top, text="LỚP HỌC",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(side="left")

        role = self.app.current_user.role
        if role in ("ADMIN", "MANAGER"):
            ctk.CTkButton(top, text="＋  Tạo lớp mới",
                          font=ctk.CTkFont(size=11, weight="bold"),
                          fg_color=ORANGE, hover_color=ORANGE_DARK,
                          height=40, corner_radius=12,
                          command=self._open_add_dialog).pack(side="right")

        sf = ctk.CTkFrame(top, fg_color=WHITE, corner_radius=12,
                           border_width=1, border_color=BORDER)
        sf.pack(side="right", padx=(0, 12))
        ctk.CTkLabel(sf, text="🔍").pack(side="left", padx=(12, 0))
        ctk.CTkEntry(sf, textvariable=self.search_var,
                     placeholder_text="Tìm lớp học...",
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
        classes = [c for c in self.app.data["classes"]
                   if not term or term in c.name.lower()]

        if not classes:
            ctk.CTkLabel(self.scroll, text="Chưa có lớp học nào",
                         font=ctk.CTkFont(size=13), text_color=TEXT_MUTED).pack(pady=60)
            return

        COLS = 3
        for i, cls in enumerate(classes):
            col = i % COLS
            row = i // COLS
            self.scroll.grid_columnconfigure(col, weight=1)

            trainer = next((u for u in self.app.data["users"] if u.id == cls.trainerId), None)
            trainer_name = trainer.fullName if trainer else "Chưa phân công"
            enrolled = len(cls.enrolledMemberIds)
            is_full = enrolled >= cls.capacity

            card = ctk.CTkFrame(self.scroll, fg_color=WHITE, corner_radius=20,
                                 border_width=1, border_color=BORDER)
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

            # Header
            hdr = ctk.CTkFrame(card, fg_color=ORANGE if not is_full else "#f1f5f9",
                                corner_radius=12)
            hdr.pack(fill="x", padx=12, pady=(12, 0))
            ctk.CTkLabel(hdr, text=cls.name.upper(),
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=WHITE if not is_full else TEXT_MUTED).pack(anchor="w", padx=16, pady=(12, 0))
            ctk.CTkLabel(hdr, text=f"🗓 {cls.dayOfWeek}  🕐 {cls.time}",
                         font=ctk.CTkFont(size=11),
                         text_color=WHITE if not is_full else TEXT_SECONDARY).pack(anchor="w", padx=16, pady=(2, 12))

            detail = ctk.CTkFrame(card, fg_color="#f8fafc", corner_radius=12,
                                   border_width=1, border_color=BORDER)
            detail.pack(fill="x", padx=12, pady=8)
            rows_data = [
                ("🏋️ HLV", trainer_name),
                ("👥 Học viên", f"{enrolled}/{cls.capacity}"),
                ("📊 Trạng thái", "Đầy" if is_full else "Còn chỗ"),
            ]
            for ri, (lbl, val) in enumerate(rows_data):
                detail.grid_columnconfigure(1, weight=1)
                ctk.CTkLabel(detail, text=lbl,
                             font=ctk.CTkFont(size=9, weight="bold"),
                             text_color=TEXT_MUTED).grid(row=ri, column=0, padx=12, pady=5, sticky="w")
                ctk.CTkLabel(detail, text=val,
                             font=ctk.CTkFont(size=11, weight="bold"),
                             text_color=RED if val == "Đầy" else TEXT_PRIMARY).grid(row=ri, column=1, padx=12, pady=5, sticky="e")

            role = self.app.current_user.role
            if role in ("ADMIN", "MANAGER"):
                btn_row = ctk.CTkFrame(card, fg_color=WHITE, corner_radius=0)
                btn_row.pack(fill="x", padx=12, pady=(0, 12))
                btn_row.grid_columnconfigure((0, 1), weight=1)
                ctk.CTkButton(btn_row, text="✏ Sửa",
                              fg_color="#f1f5f9", text_color=TEXT_SECONDARY,
                              hover_color="#dbeafe", corner_radius=10, height=34,
                              font=ctk.CTkFont(size=11, weight="bold"),
                              command=lambda c=cls: self._open_edit_dialog(c)).grid(row=0, column=0, sticky="ew", padx=(0, 4))
                ctk.CTkButton(btn_row, text="🗑 Xóa",
                              fg_color="#f1f5f9", text_color=TEXT_SECONDARY,
                              hover_color="#fee2e2", corner_radius=10, height=34,
                              font=ctk.CTkFont(size=11, weight="bold"),
                              command=lambda c=cls: self._confirm_delete(c)).grid(row=0, column=1, sticky="ew", padx=(4, 0))

    def _open_add_dialog(self):
        ClassFormDialog(self, app=self.app, on_save=self._save_add)

    def _open_edit_dialog(self, cls):
        ClassFormDialog(self, app=self.app, cls=cls, on_save=self._save_edit)

    def _save_add(self, data):
        cls = ClassSession(
            id=str(int(time.time() * 1000)),
            name=data["name"], trainerId=data["trainerId"],
            time=data["time"], dayOfWeek=data["dayOfWeek"],
            capacity=int(data["capacity"] or 20)
        )
        try:
            cs.add(cls)
            self.app.data["classes"].append(cls)
            self._refresh()
            self.app.show_notification(f"Đã tạo lớp: {cls.name}", "success")
        except Exception as e:
            self.app.show_notification(f"Lỗi: {e}", "error")

    def _save_edit(self, data):
        cls = data["__cls__"]
        cls.name = data["name"]
        cls.trainerId = data["trainerId"]
        cls.time = data["time"]
        cls.dayOfWeek = data["dayOfWeek"]
        cls.capacity = int(data["capacity"] or cls.capacity)
        try:
            cs.update(cls)
            self._refresh()
            self.app.show_notification("Đã cập nhật lớp học", "success")
        except Exception as e:
            self.app.show_notification(f"Lỗi: {e}", "error")

    def _confirm_delete(self, cls):
        dlg = ctk.CTkToplevel(self)
        dlg.title("Xóa lớp học")
        dlg.geometry("320x180")
        dlg.grab_set()
        dlg.configure(fg_color=WHITE)
        ctk.CTkLabel(dlg, text=f"Xóa lớp '{cls.name}'?",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(28, 8))
        row = ctk.CTkFrame(dlg, fg_color=WHITE)
        row.pack(fill="x", padx=24, pady=16)
        ctk.CTkButton(row, text="Hủy", fg_color="#f1f5f9",
                       text_color=TEXT_SECONDARY,
                       command=dlg.destroy).pack(side="left", expand=True, fill="x", padx=(0, 6))
        ctk.CTkButton(row, text="Xóa", fg_color=RED, text_color=WHITE,
                       command=lambda: [dlg.destroy(), self._do_delete(cls)]).pack(side="left", expand=True, fill="x", padx=(6, 0))

    def _do_delete(self, cls):
        try:
            cs.delete(cls.id)
            self.app.data["classes"] = [c for c in self.app.data["classes"] if c.id != cls.id]
            self._refresh()
            self.app.show_notification("Đã hủy lớp học", "success")
        except Exception as e:
            self.app.show_notification(f"Lỗi: {e}", "error")


class ClassFormDialog(ctk.CTkToplevel):
    def __init__(self, master, app, on_save, cls: ClassSession = None):
        super().__init__(master)
        self.title("Lớp học")
        self.geometry("440x440")
        self.resizable(False, False)
        self.grab_set()
        self.configure(fg_color=WHITE)
        self.app = app
        self.cls = cls
        self.on_save = on_save
        self._build()

    def _build(self):
        c = self.cls
        title = "Cập nhật lớp học" if c else "Tạo lớp học mới"
        ctk.CTkLabel(self, text=title.upper(),
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=24, pady=(24, 12))

        def field(label, default=""):
            ctk.CTkLabel(self, text=label,
                         font=ctk.CTkFont(size=9, weight="bold"),
                         text_color=TEXT_MUTED).pack(anchor="w", padx=24, pady=(8, 2))
            entry = ctk.CTkEntry(self, height=44, corner_radius=10,
                                  border_color=BORDER, border_width=1,
                                  fg_color="#f8fafc", text_color=TEXT_PRIMARY,
                                  font=ctk.CTkFont(size=13, weight="bold"))
            entry.pack(fill="x", padx=24)
            if default:
                entry.insert(0, str(default))
            return entry

        self._name = field("TÊN LỚP HỌC *", c.name if c else "")
        self._time = field("GIỜ HỌC (VD: 07:00)", c.time if c else "")
        self._day = field("NGÀY TRONG TUẦN", c.dayOfWeek if c else "")
        self._cap = field("SỨC CHỨA", c.capacity if c else "20")

        ctk.CTkLabel(self, text="HUẤN LUYỆN VIÊN *",
                     font=ctk.CTkFont(size=9, weight="bold"),
                     text_color=TEXT_MUTED).pack(anchor="w", padx=24, pady=(8, 2))
        trainers = [u for u in self.app.data["users"] if u.role == "PT"]
        trainer_names = [t.fullName for t in trainers]
        self._trainers = trainers
        self._trainer_combo = ctk.CTkComboBox(self, values=trainer_names, height=44,
                                               corner_radius=10, border_color=BORDER,
                                               fg_color="#f8fafc", text_color=TEXT_PRIMARY,
                                               font=ctk.CTkFont(size=13, weight="bold"),
                                               button_color=ORANGE)
        self._trainer_combo.pack(fill="x", padx=24)
        if c:
            t = next((u for u in trainers if u.id == c.trainerId), None)
            if t:
                self._trainer_combo.set(t.fullName)

        sep = ctk.CTkFrame(self, fg_color=BORDER, height=1, corner_radius=0)
        sep.pack(fill="x", pady=(16, 0))
        foot = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=0, height=70)
        foot.pack(fill="x")
        foot.pack_propagate(False)
        foot.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(foot, text="Hủy", fg_color="#f1f5f9",
                       text_color=TEXT_SECONDARY, height=44, corner_radius=12,
                       command=self.destroy).grid(row=0, column=0, padx=(24, 6), pady=13, sticky="ew")
        ctk.CTkButton(foot, text="Lưu lớp học", fg_color=ORANGE, hover_color=ORANGE_DARK,
                       text_color=WHITE, height=44, corner_radius=12,
                       command=self._submit).grid(row=0, column=1, padx=(6, 24), pady=13, sticky="ew")

    def _submit(self):
        trainer_name = self._trainer_combo.get()
        trainer = next((u for u in self._trainers if u.fullName == trainer_name), None)
        data = {
            "name": self._name.get().strip(),
            "time": self._time.get().strip(),
            "dayOfWeek": self._day.get().strip(),
            "capacity": self._cap.get().strip(),
            "trainerId": trainer.id if trainer else "",
        }
        if not data["name"]:
            return
        if self.cls:
            data["__cls__"] = self.cls
        self.destroy()
        self.on_save(data)
