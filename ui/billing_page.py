"""
Tài chính / Billing Page
"""
import customtkinter as ctk
import time
from datetime import date
from models.models import Invoice, InvoiceItem
import services.invoice_service as ivs
from ui.app import (ORANGE, ORANGE_DARK, ORANGE_LIGHT, WHITE, BG,
                     TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, BORDER, EMERALD, RED, BLUE)


class BillingPage(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, fg_color=BG, corner_radius=0, **kwargs)
        self.app = app
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", lambda *a: self._refresh_table())
        self._build()

    def _build(self):
        # Top
        top = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        top.pack(fill="x", padx=24, pady=(20, 0))

        ctk.CTkLabel(top, text="TÀI CHÍNH",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(side="left")

        ctk.CTkButton(top, text="＋  Tạo hóa đơn",
                      font=ctk.CTkFont(size=11, weight="bold"),
                      fg_color=ORANGE, hover_color=ORANGE_DARK,
                      height=40, corner_radius=12,
                      command=self._open_create_dialog).pack(side="right")

        search_frame = ctk.CTkFrame(top, fg_color=WHITE, corner_radius=12,
                                     border_width=1, border_color=BORDER)
        search_frame.pack(side="right", padx=12)
        ctk.CTkLabel(search_frame, text="🔍").pack(side="left", padx=(12, 0))
        ctk.CTkEntry(search_frame, textvariable=self.search_var,
                     placeholder_text="Tìm hóa đơn...",
                     width=200, height=38, border_width=0,
                     fg_color=WHITE, text_color=TEXT_PRIMARY,
                     font=ctk.CTkFont(size=12)).pack(side="left", padx=8)

        # Stats
        invoices = self.app.data["invoices"]
        total_rev = sum(i.total for i in invoices)
        today_rev = sum(i.total for i in invoices if i.date[:10] == date.today().isoformat())

        stats = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        stats.pack(fill="x", padx=24, pady=12)
        stat_data = [
            ("💰 Tổng doanh thu", f"{total_rev:,.0f} đ", ORANGE),
            ("📅 Doanh thu hôm nay", f"{today_rev:,.0f} đ", EMERALD),
            ("🧾 Số hóa đơn", str(len(invoices)), BLUE),
        ]
        for label, val, color in stat_data:
            card = ctk.CTkFrame(stats, fg_color=WHITE, corner_radius=16,
                                 border_width=1, border_color=BORDER)
            card.pack(side="left", padx=(0, 12), ipadx=16, ipady=10)
            ctk.CTkLabel(card, text=label,
                         font=ctk.CTkFont(size=9, weight="bold"),
                         text_color=TEXT_MUTED).pack(anchor="w", padx=16, pady=(10, 0))
            ctk.CTkLabel(card, text=val,
                         font=ctk.CTkFont(size=18, weight="bold"),
                         text_color=color).pack(anchor="w", padx=16, pady=(0, 10))

        # Table
        table_card = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=20,
                                   border_width=1, border_color=BORDER)
        table_card.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        table_card.grid_rowconfigure(1, weight=1)
        table_card.grid_columnconfigure(0, weight=1)

        # Table header
        cols = ["Mã HĐ", "Hội viên", "Ngày", "Tổng tiền", "Phương thức", "Sản phẩm"]
        widths = [100, 180, 100, 130, 120, 250]
        hdr = ctk.CTkFrame(table_card, fg_color="#f8fafc", corner_radius=0,
                            border_width=0)
        hdr.grid(row=0, column=0, sticky="ew", padx=0)
        for ci, (col, w) in enumerate(zip(cols, widths)):
            ctk.CTkLabel(hdr, text=col.upper(),
                         font=ctk.CTkFont(size=8, weight="bold"),
                         text_color=TEXT_MUTED, width=w, anchor="w").grid(
                row=0, column=ci, padx=(16 if ci == 0 else 8, 0), pady=10, sticky="w")

        self.scroll = ctk.CTkScrollableFrame(table_card, fg_color=WHITE,
                                              corner_radius=0,
                                              scrollbar_button_color=BORDER)
        self.scroll.grid(row=1, column=0, sticky="nsew")

        self._refresh_table()

    def _refresh_table(self):
        for w in self.scroll.winfo_children():
            w.destroy()
        term = self.search_var.get().lower()
        members_map = {m.id: m for m in self.app.data["members"]}
        invoices = self.app.data["invoices"]
        invoices = sorted(invoices, key=lambda i: i.date, reverse=True)

        for inv in invoices:
            member = members_map.get(inv.memberId)
            mname = member.fullName if member else inv.memberId
            if term and term not in mname.lower() and term not in inv.id.lower():
                continue

            row = ctk.CTkFrame(self.scroll, fg_color=WHITE, corner_radius=0,
                                border_width=0, border_color=BORDER)
            row.pack(fill="x")
            sep = ctk.CTkFrame(self.scroll, fg_color=BORDER, height=1, corner_radius=0)
            sep.pack(fill="x")

            items_text = ", ".join(f"{it.name}×{it.quantity}" for it in inv.items)
            vals = [inv.id[:10] + "...", mname, inv.date[:10],
                    f"{inv.total:,.0f} đ", inv.method, items_text]
            widths = [100, 180, 100, 130, 120, 250]
            for ci, (val, w) in enumerate(zip(vals, widths)):
                color = ORANGE if ci == 3 else (EMERALD if ci == 4 else TEXT_PRIMARY)
                ctk.CTkLabel(row, text=val,
                             font=ctk.CTkFont(size=11, weight="bold" if ci == 3 else "normal"),
                             text_color=color, width=w, anchor="w",
                             wraplength=w).grid(
                    row=0, column=ci, padx=(16 if ci == 0 else 8, 0), pady=10, sticky="w")

    def _open_create_dialog(self):
        InvoiceDialog(self, app=self.app, on_save=self._save_invoice)

    def _save_invoice(self, data):
        invoice = Invoice(
            id=str(int(time.time() * 1000)),
            memberId=data["memberId"],
            items=data["items"],
            total=data["total"],
            date=date.today().isoformat(),
            method=data["method"]
        )
        try:
            ivs.create(invoice)
            self.app.data["invoices"].insert(0, invoice)
            self._refresh_table()
            self.app.show_notification("Đã tạo hóa đơn thành công", "success")
        except Exception as e:
            self.app.show_notification(f"Lỗi: {e}", "error")


class InvoiceDialog(ctk.CTkToplevel):
    def __init__(self, master, app, on_save):
        super().__init__(master)
        self.title("Tạo hóa đơn mới")
        self.geometry("560x620")
        self.resizable(False, True)
        self.grab_set()
        self.configure(fg_color=WHITE)
        self.app = app
        self.on_save = on_save
        self.items: list[InvoiceItem] = []
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="TẠO HÓA ĐƠN",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=24, pady=(24, 0))

        body = ctk.CTkScrollableFrame(self, fg_color=WHITE, corner_radius=0)
        body.pack(fill="both", expand=True)

        # Member
        ctk.CTkLabel(body, text="HỘI VIÊN *",
                     font=ctk.CTkFont(size=9, weight="bold"),
                     text_color=TEXT_MUTED).pack(anchor="w", padx=24, pady=(12, 2))
        member_names = [m.fullName for m in self.app.data["members"]]
        self.member_combo = ctk.CTkComboBox(body, values=member_names, height=44,
                                             corner_radius=10, border_color=BORDER,
                                             fg_color="#f8fafc", text_color=TEXT_PRIMARY,
                                             font=ctk.CTkFont(size=13, weight="bold"),
                                             button_color=ORANGE)
        self.member_combo.pack(fill="x", padx=24)

        # Payment method
        ctk.CTkLabel(body, text="PHƯƠNG THỨC THANH TOÁN",
                     font=ctk.CTkFont(size=9, weight="bold"),
                     text_color=TEXT_MUTED).pack(anchor="w", padx=24, pady=(16, 4))
        self.method_var = ctk.StringVar(value="CASH")
        mf = ctk.CTkFrame(body, fg_color="#f1f5f9", corner_radius=12)
        mf.pack(fill="x", padx=24)
        for method in ("CASH", "TRANSFER", "E-WALLET"):
            ctk.CTkRadioButton(mf, text=method, variable=self.method_var, value=method,
                                fg_color=ORANGE, hover_color=ORANGE_DARK,
                                font=ctk.CTkFont(size=12, weight="bold"),
                                text_color=TEXT_PRIMARY).pack(side="left", padx=16, pady=10)

        # Add item
        ctk.CTkLabel(body, text="THÊM SẢN PHẨM / DỊCH VỤ",
                     font=ctk.CTkFont(size=9, weight="bold"),
                     text_color=TEXT_MUTED).pack(anchor="w", padx=24, pady=(16, 4))

        item_row = ctk.CTkFrame(body, fg_color="transparent", corner_radius=0)
        item_row.pack(fill="x", padx=24)
        item_row.grid_columnconfigure(0, weight=3)
        item_row.grid_columnconfigure(1, weight=1)
        item_row.grid_columnconfigure(2, weight=1)

        # Product combo
        product_names = [p.name for p in self.app.data["products"]]
        plan_names = [f"[Gói] {p.name}" for p in self.app.data["plans"]]
        all_items = product_names + plan_names
        self.item_combo = ctk.CTkComboBox(item_row, values=all_items, height=40,
                                           corner_radius=8, border_color=BORDER,
                                           fg_color="#f8fafc", text_color=TEXT_PRIMARY,
                                           font=ctk.CTkFont(size=12),
                                           button_color=ORANGE)
        self.item_combo.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.qty_entry = ctk.CTkEntry(item_row, placeholder_text="SL",
                                       height=40, corner_radius=8,
                                       border_color=BORDER, border_width=1,
                                       fg_color="#f8fafc", text_color=TEXT_PRIMARY)
        self.qty_entry.grid(row=0, column=1, sticky="ew", padx=(0, 8))
        self.qty_entry.insert(0, "1")

        self.price_entry = ctk.CTkEntry(item_row, placeholder_text="Giá",
                                         height=40, corner_radius=8,
                                         border_color=BORDER, border_width=1,
                                         fg_color="#f8fafc", text_color=TEXT_PRIMARY)
        self.price_entry.grid(row=0, column=2, sticky="ew")

        ctk.CTkButton(body, text="＋  Thêm dòng",
                      fg_color="#f1f5f9", text_color=TEXT_SECONDARY,
                      hover_color=ORANGE_LIGHT, height=36, corner_radius=8,
                      font=ctk.CTkFont(size=11, weight="bold"),
                      command=self._add_item).pack(fill="x", padx=24, pady=8)

        # Items list
        self.items_frame = ctk.CTkFrame(body, fg_color="#f8fafc", corner_radius=12,
                                         border_width=1, border_color=BORDER)
        self.items_frame.pack(fill="x", padx=24)

        ctk.CTkLabel(body, text="",
                     font=ctk.CTkFont(size=12)).pack()
        self.total_lbl = ctk.CTkLabel(body, text="TỔNG CỘNG: 0 đ",
                                       font=ctk.CTkFont(size=16, weight="bold"),
                                       text_color=ORANGE)
        self.total_lbl.pack(padx=24, pady=8)

        # Footer
        sep = ctk.CTkFrame(self, fg_color=BORDER, height=1, corner_radius=0)
        sep.pack(fill="x")
        foot = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=0, height=72)
        foot.pack(fill="x")
        foot.pack_propagate(False)
        foot.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(foot, text="Hủy", fg_color="#f1f5f9",
                       text_color=TEXT_SECONDARY, hover_color=BORDER,
                       font=ctk.CTkFont(weight="bold"), height=44, corner_radius=12,
                       command=self.destroy).grid(row=0, column=0, padx=(24, 6), pady=14, sticky="ew")
        ctk.CTkButton(foot, text="✓  Lưu hóa đơn",
                       fg_color=ORANGE, hover_color=ORANGE_DARK,
                       text_color=WHITE, font=ctk.CTkFont(weight="bold"),
                       height=44, corner_radius=12,
                       command=self._submit).grid(row=0, column=1, padx=(6, 24), pady=14, sticky="ew")

    def _add_item(self):
        name = self.item_combo.get().strip()
        try:
            qty = int(self.qty_entry.get())
        except ValueError:
            qty = 1
        try:
            price = float(self.price_entry.get().replace(",", ""))
        except ValueError:
            # Auto-fill price from product
            prod = next((p for p in self.app.data["products"] if p.name == name), None)
            if not prod:
                plan = next((p for p in self.app.data["plans"] if f"[Gói] {p.name}" == name), None)
                price = plan.price if plan else 0
            else:
                price = prod.price

        if not name:
            return
        item = InvoiceItem(name=name, quantity=qty, price=price)
        self.items.append(item)
        self._refresh_items()

    def _refresh_items(self):
        for w in self.items_frame.winfo_children():
            w.destroy()
        total = 0
        for i, item in enumerate(self.items):
            subtotal = item.quantity * item.price
            total += subtotal
            row = ctk.CTkFrame(self.items_frame, fg_color="transparent", corner_radius=0)
            row.pack(fill="x", padx=12, pady=3)
            ctk.CTkLabel(row, text=f"{item.name}",
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=TEXT_PRIMARY).pack(side="left")
            ctk.CTkLabel(row, text=f"×{item.quantity}  {item.price:,.0f}đ = {subtotal:,.0f}đ",
                         font=ctk.CTkFont(size=11),
                         text_color=TEXT_SECONDARY).pack(side="right")
        self.total_lbl.configure(text=f"TỔNG CỘNG: {total:,.0f} đ")

    def _submit(self):
        if not self.items:
            return
        member_name = self.member_combo.get()
        member = next((m for m in self.app.data["members"] if m.fullName == member_name), None)
        if not member:
            return
        total = sum(it.quantity * it.price for it in self.items)
        data = {
            "memberId": member.id,
            "items": self.items,
            "total": total,
            "method": self.method_var.get()
        }
        self.destroy()
        self.on_save(data)
