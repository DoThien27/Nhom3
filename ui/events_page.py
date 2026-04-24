import customtkinter as ctk
from datetime import datetime
import uuid

from ui.app import (ORANGE, ORANGE_LIGHT, WHITE, BG, TEXT_PRIMARY,
                     TEXT_SECONDARY, TEXT_MUTED, BORDER, EMERALD, RED, BLUE)
from models.models import Event, EventParticipant
import services.event_service as evs


class EventsPage(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, fg_color=BG, corner_radius=0, **kwargs)
        self.app = app
        self.events = self.app.data.get("events", [])
        
        self._build_layout()
        self._load_events()

    def _build_layout(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Top Bar
        top_bar = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        top_bar.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 16))
        top_bar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(top_bar, text="Danh Sách Sự Kiện",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=TEXT_PRIMARY).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(top_bar, text="+ Thêm Sự Kiện",
                      font=ctk.CTkFont(weight="bold"), fg_color=ORANGE,
                      text_color=WHITE, hover_color="#ea6c0a",
                      command=self._show_event_form).grid(row=0, column=2, sticky="e")

        # Main Content
        self.main_content = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=16,
                                         border_width=1, border_color=BORDER)
        self.main_content.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(1, weight=1)

        # Header Row
        headers = ctk.CTkFrame(self.main_content, fg_color="#f8fafc", corner_radius=0, height=48)
        headers.grid(row=0, column=0, sticky="ew")
        headers.grid_propagate(False)

        cols = [
            ("TÊN SỰ KIỆN", 0.25),
            ("NGÀY/GIỜ", 0.15),
            ("ĐỊA ĐIỂM", 0.2),
            ("SỨC CHỨA", 0.1),
            ("TRẠNG THÁI", 0.15),
            ("THAO TÁC", 0.15)
        ]

        for i, (text, weight) in enumerate(cols):
            headers.grid_columnconfigure(i, weight=int(weight * 100))
            ctk.CTkLabel(headers, text=text,
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=TEXT_SECONDARY).grid(row=0, column=i, sticky="w", padx=16, pady=12)

        # List Frame
        self.list_frame = ctk.CTkScrollableFrame(self.main_content, fg_color="transparent", corner_radius=0)
        self.list_frame.grid(row=1, column=0, sticky="nsew")
        for i, (_, weight) in enumerate(cols):
            self.list_frame.grid_columnconfigure(i, weight=int(weight * 100))

    def _load_events(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        self.events = evs.get_all_events()
        self.app.data["events"] = self.events

        if not self.events:
            ctk.CTkLabel(self.list_frame, text="Chưa có sự kiện nào.",
                         text_color=TEXT_MUTED).grid(row=0, column=0, columnspan=6, pady=40)
            return

        for idx, event in enumerate(self.events):
            row_frame = ctk.CTkFrame(self.list_frame, fg_color="transparent", corner_radius=0, height=60)
            row_frame.grid(row=idx, column=0, columnspan=6, sticky="ew", pady=2)
            row_frame.grid_propagate(False)
            
            for i, (_, weight) in enumerate([("a", 0.25), ("b", 0.15), ("c", 0.2), ("d", 0.1), ("e", 0.15), ("f", 0.15)]):
                row_frame.grid_columnconfigure(i, weight=int(weight * 100))

            # Name
            name_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            name_frame.grid(row=0, column=0, sticky="w", padx=16, pady=12)
            ctk.CTkLabel(name_frame, text=event.name,
                         font=ctk.CTkFont(weight="bold"), text_color=TEXT_PRIMARY).pack(anchor="w")

            # Date/Time
            ctk.CTkLabel(row_frame, text=f"{event.date} {event.time}",
                         text_color=TEXT_SECONDARY).grid(row=0, column=1, sticky="w", padx=16)

            # Location
            ctk.CTkLabel(row_frame, text=event.location,
                         text_color=TEXT_SECONDARY).grid(row=0, column=2, sticky="w", padx=16)

            # Capacity
            ctk.CTkLabel(row_frame, text=str(event.capacity),
                         text_color=TEXT_SECONDARY).grid(row=0, column=3, sticky="w", padx=16)

            # Status
            status_color = EMERALD if event.status == "UPCOMING" else (TEXT_SECONDARY if event.status == "COMPLETED" else RED)
            ctk.CTkLabel(row_frame, text=event.status,
                         font=ctk.CTkFont(weight="bold"), text_color=status_color).grid(row=0, column=4, sticky="w", padx=16)

            # Actions
            action_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            action_frame.grid(row=0, column=5, sticky="w", padx=16)
            
            ctk.CTkButton(action_frame, text="Duyệt", width=60, height=28, fg_color=BLUE,
                          command=lambda e=event: self._show_participants(e)).pack(side="left", padx=(0, 4))
            ctk.CTkButton(action_frame, text="Sửa", width=50, height=28, fg_color=ORANGE,
                          command=lambda e=event: self._show_event_form(e)).pack(side="left", padx=(0, 4))
            ctk.CTkButton(action_frame, text="Xóa", width=50, height=28, fg_color=RED,
                          command=lambda e=event: self._delete_event(e)).pack(side="left")

    def _show_event_form(self, event=None):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Sự Kiện" if event else "Thêm Sự Kiện")
        dialog.geometry("400x550")
        dialog.grab_set()
        
        container = ctk.CTkFrame(dialog, fg_color=WHITE, corner_radius=0)
        container.pack(fill="both", expand=True)

        ctk.CTkLabel(container, text="Thông Tin Sự Kiện", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(20, 10))

        entries = {}
        fields = [
            ("name", "Tên Sự Kiện"),
            ("description", "Mô tả"),
            ("date", "Ngày (YYYY-MM-DD)"),
            ("time", "Giờ (HH:MM)"),
            ("location", "Địa điểm"),
            ("capacity", "Sức chứa")
        ]

        for key, label in fields:
            ctk.CTkLabel(container, text=label).pack(anchor="w", padx=20, pady=(10, 0))
            entry = ctk.CTkEntry(container)
            entry.pack(fill="x", padx=20, pady=(2, 0))
            entries[key] = entry
            
            if event:
                val = getattr(event, key)
                entry.insert(0, str(val))
        
        if event:
            ctk.CTkLabel(container, text="Trạng thái").pack(anchor="w", padx=20, pady=(10, 0))
            status_cb = ctk.CTkComboBox(container, values=["UPCOMING", "ONGOING", "COMPLETED", "CANCELLED"])
            status_cb.set(event.status)
            status_cb.pack(fill="x", padx=20, pady=(2, 0))
            entries["status"] = status_cb

        def save():
            try:
                name = entries["name"].get()
                date = entries["date"].get()
                time = entries["time"].get()
                
                if not name or not date or not time:
                    self.app.show_notification("Tên, ngày, giờ là bắt buộc!", "error")
                    return
                
                capacity = int(entries["capacity"].get() or 0)
                
                if event:
                    event.name = name
                    event.description = entries["description"].get()
                    event.date = date
                    event.time = time
                    event.location = entries["location"].get()
                    event.capacity = capacity
                    event.status = entries["status"].get()
                    evs.update_event(event)
                    self.app.show_notification("Cập nhật thành công!", "success")
                else:
                    new_evt = Event(
                        id=str(uuid.uuid4()),
                        name=name,
                        description=entries["description"].get(),
                        date=date,
                        time=time,
                        location=entries["location"].get(),
                        capacity=capacity,
                        status="UPCOMING"
                    )
                    evs.add_event(new_evt)
                    self.app.show_notification("Thêm mới thành công!", "success")
                
                dialog.destroy()
                self._load_events()
            except Exception as e:
                self.app.show_notification(f"Lỗi: {e}", "error")

        ctk.CTkButton(container, text="Lưu", command=save, fg_color=ORANGE).pack(pady=20)

    def _delete_event(self, event):
        if evs.delete_event(event.id):
            self.app.show_notification("Đã xóa sự kiện!", "success")
            self._load_events()
        else:
            self.app.show_notification("Lỗi khi xóa!", "error")

    def _show_participants(self, event):
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Duyệt tham gia: {event.name}")
        dialog.geometry("600x400")
        dialog.grab_set()
        
        container = ctk.CTkFrame(dialog, fg_color=WHITE, corner_radius=0)
        container.pack(fill="both", expand=True)

        top = ctk.CTkFrame(container, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(top, text=f"Người Tham Gia - {event.name}", 
                     font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        
        list_frame = ctk.CTkScrollableFrame(container, fg_color=BG)
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        def load_parts():
            for w in list_frame.winfo_children():
                w.destroy()
            
            parts = evs.get_participants_for_event(event.id)
            if not parts:
                ctk.CTkLabel(list_frame, text="Chưa có ai đăng ký.").pack(pady=20)
                return
            
            for p in parts:
                f = ctk.CTkFrame(list_frame, fg_color=WHITE, corner_radius=8)
                f.pack(fill="x", pady=4, padx=4)
                
                ctk.CTkLabel(f, text=p.memberName, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10, pady=10)
                
                stat_col = ORANGE if p.status == "PENDING" else (EMERALD if p.status == "APPROVED" else RED)
                ctk.CTkLabel(f, text=p.status, text_color=stat_col).pack(side="left", padx=10)
                
                if p.status == "PENDING":
                    ctk.CTkButton(f, text="Từ chối", width=60, fg_color=RED,
                                  command=lambda pt=p: update_pt(pt, "REJECTED")).pack(side="right", padx=(0, 10))
                    ctk.CTkButton(f, text="Duyệt", width=60, fg_color=EMERALD,
                                  command=lambda pt=p: update_pt(pt, "APPROVED")).pack(side="right", padx=(0, 10))

        def update_pt(pt, status):
            if evs.update_participant_status(pt.id, status):
                self.app.show_notification(f"Đã {status} cho {pt.memberName}", "success")
                load_parts()
            else:
                self.app.show_notification("Lỗi cập nhật", "error")

        load_parts()
