"""
Kho & Thiết bị — Inventory Page
"""
import customtkinter as ctk
import time
from models.models import Product
import services.product_service as prs
from ui.app import (ORANGE, ORANGE_DARK, ORANGE_LIGHT, WHITE, BG,
                     TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, BORDER, EMERALD, RED, BLUE)


class InventoryPage(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, fg_color=BG, corner_radius=0, **kwargs)
        self.app = app
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", lambda *a: self._refresh_table())
        self.filter_var = ctk.StringVar(value="TẤT CẢ")
        self.filter_var.trace("w", lambda *a: self._refresh_table())
        self._build()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        top.pack(fill="x", padx=24, pady=(20, 0))

        ctk.CTkLabel(top, text="KHO & THIẾT BỊ",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(side="left")

        ctk.CTkButton(top, text="＋  Thêm sản phẩm",
                      font=ctk.CTkFont(size=11, weight="bold"),
                      fg_color=ORANGE, hover_color=ORANGE_DARK,
                      height=40, corner_radius=12,
                      command=self._open_add_dialog).pack(side="right")

        # Filter tabs
        tabs = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=12,
                             border_width=1, border_color=BORDER)
        tabs.pack(fill="x", padx=24, pady=12)
        for cat in ("TẤT CẢ", "EQUIPMENT", "SUPPLEMENT", "DRINK"):
            ctk.CTkButton(tabs, text=cat,
                          font=ctk.CTkFont(size=11, weight="bold"),
                          fg_color=ORANGE if self.filter_var.get() == cat else "transparent",
                          text_color=WHITE if self.filter_var.get() == cat else TEXT_SECONDARY,
                          hover_color=ORANGE_LIGHT, height=36, corner_radius=8,
                          command=lambda c=cat: self._set_filter(c)).pack(side="left", padx=4, pady=4)

        # Table
        table_card = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=20,
                                   border_width=1, border_color=BORDER)
        table_card.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        table_card.grid_rowconfigure(1, weight=1)
        table_card.grid_columnconfigure(0, weight=1)

        cols = ["Tên sản phẩm", "Danh mục", "Giá", "Tồn kho", "Cảnh báo", "Trạng thái", ""]
        widths = [200, 120, 120, 100, 100, 120, 150]
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

    def _set_filter(self, cat):
        self.filter_var.set(cat)
        # Re-build filter tabs highlight
        self._build  # Will be re-called via trace, but need to update button colors
        # Simple approach: rebuild
        for w in self.winfo_children():
            w.destroy()
        self._build()

    def _refresh_table(self):
        for w in self.scroll.winfo_children():
            w.destroy()
        term = self.search_var.get().lower()
        cat_filter = self.filter_var.get()

        for p in self.app.data["products"]:
            if term and term not in p.name.lower():
                continue
            if cat_filter != "TẤT CẢ" and p.category != cat_filter:
                continue

            is_low = p.stock <= p.minStockAlert
            row = ctk.CTkFrame(self.scroll, fg_color=WHITE, corner_radius=0,
                                border_width=0)
            row.pack(fill="x")
            sep = ctk.CTkFrame(self.scroll, fg_color=BORDER, height=1, corner_radius=0)
            sep.pack(fill="x")

            widths = [200, 120, 120, 100, 100, 120, 150]
            vals = [p.name, p.category, f"{p.price:,.0f} đ",
                    str(p.stock), str(p.minStockAlert),
                    "⚠ Sắp hết" if is_low else "✓ Đủ hàng"]
            colors = [TEXT_PRIMARY, TEXT_SECONDARY, ORANGE,
                      RED if is_low else TEXT_PRIMARY, TEXT_MUTED,
                      RED if is_low else EMERALD]
            for ci, (val, w, color) in enumerate(zip(vals, widths, colors)):
                ctk.CTkLabel(row, text=val,
                             font=ctk.CTkFont(size=11, weight="bold" if ci in (0, 3) else "normal"),
                             text_color=color, width=w, anchor="w").grid(
                    row=0, column=ci, padx=(16 if ci == 0 else 8, 0), pady=10, sticky="w")

            # Action buttons
            btn_frame = ctk.CTkFrame(row, fg_color=WHITE, corner_radius=0)
            btn_frame.grid(row=0, column=6, padx=8, pady=6, sticky="e")
            ctk.CTkButton(btn_frame, text="✏",
                          fg_color="#f1f5f9", text_color=TEXT_SECONDARY,
                          hover_color="#dbeafe", width=32, height=32, corner_radius=8,
                          command=lambda pr=p: self._open_edit_dialog(pr)).pack(side="left", padx=2)
            ctk.CTkButton(btn_frame, text="🗑",
                          fg_color="#f1f5f9", text_color=TEXT_SECONDARY,
                          hover_color="#fee2e2", width=32, height=32, corner_radius=8,
                          command=lambda pr=p: self._confirm_delete(pr)).pack(side="left", padx=2)

    def _open_add_dialog(self):
        ProductFormDialog(self, on_save=self._save_add)

    def _open_edit_dialog(self, product):
        ProductFormDialog(self, product=product, on_save=self._save_edit)

    def _save_add(self, data):
        prod = Product(
            id=str(int(time.time() * 1000)),
            name=data["name"], category=data["category"],
            price=float(data["price"] or 0),
            stock=int(data["stock"] or 0),
            minStockAlert=int(data["minStockAlert"] or 0)
        )
        try:
            prs.add(prod)
            self.app.data["products"].append(prod)
            self._refresh_table()
            self.app.show_notification(f"Đã thêm: {prod.name}", "success")
        except Exception as e:
            self.app.show_notification(f"Lỗi: {e}", "error")

    def _save_edit(self, data):
        product = data["__product__"]
        product.name = data["name"]
        product.category = data["category"]
        product.price = float(data["price"] or product.price)
        product.stock = int(data["stock"] or product.stock)
        product.minStockAlert = int(data["minStockAlert"] or product.minStockAlert)
        try:
            prs.update(product)
            self._refresh_table()
            self.app.show_notification("Đã cập nhật sản phẩm", "success")
        except Exception as e:
            self.app.show_notification(f"Lỗi: {e}", "error")

    def _confirm_delete(self, product):
        dlg = ctk.CTkToplevel(self)
        dlg.title("Xóa sản phẩm")
        dlg.geometry("320x180")
        dlg.grab_set()
        dlg.configure(fg_color=WHITE)
        ctk.CTkLabel(dlg, text=f"Xóa '{product.name}'?",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(pady=(28, 8))
        row = ctk.CTkFrame(dlg, fg_color=WHITE)
        row.pack(fill="x", padx=24, pady=16)
        ctk.CTkButton(row, text="Hủy", fg_color="#f1f5f9",
                       text_color=TEXT_SECONDARY,
                       command=dlg.destroy).pack(side="left", expand=True, fill="x", padx=(0, 6))
        ctk.CTkButton(row, text="Xóa", fg_color=RED, text_color=WHITE,
                       command=lambda: [dlg.destroy(), self._do_delete(product)]).pack(side="left", expand=True, fill="x", padx=(6, 0))

    def _do_delete(self, product):
        try:
            prs.delete(product.id)
            self.app.data["products"] = [p for p in self.app.data["products"] if p.id != product.id]
            self._refresh_table()
            self.app.show_notification("Đã xóa sản phẩm", "success")
        except Exception as e:
            self.app.show_notification(f"Lỗi: {e}", "error")


class ProductFormDialog(ctk.CTkToplevel):
    def __init__(self, master, on_save, product: Product = None):
        super().__init__(master)
        self.title("Sản phẩm")
        self.geometry("440x440")
        self.resizable(False, False)
        self.grab_set()
        self.configure(fg_color=WHITE)
        self.product = product
        self.on_save = on_save
        self._build()

    def _build(self):
        p = self.product
        title = "Cập nhật sản phẩm" if p else "Thêm sản phẩm mới"
        ctk.CTkLabel(self, text=title.upper(),
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=24, pady=(24, 16))

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

        self._name = field("TÊN SẢN PHẨM *", p.name if p else "")

        ctk.CTkLabel(self, text="DANH MỤC",
                     font=ctk.CTkFont(size=9, weight="bold"),
                     text_color=TEXT_MUTED).pack(anchor="w", padx=24, pady=(8, 2))
        self._cat_var = ctk.StringVar(value=p.category if p else "EQUIPMENT")
        cat_frame = ctk.CTkFrame(self, fg_color="#f1f5f9", corner_radius=10)
        cat_frame.pack(fill="x", padx=24)
        for cat in ("EQUIPMENT", "SUPPLEMENT", "DRINK"):
            ctk.CTkRadioButton(cat_frame, text=cat, variable=self._cat_var, value=cat,
                                fg_color=ORANGE, font=ctk.CTkFont(size=11, weight="bold"),
                                text_color=TEXT_PRIMARY).pack(side="left", padx=12, pady=8)

        row = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        row.pack(fill="x", padx=24, pady=(8, 0))
        row.grid_columnconfigure((0, 1, 2), weight=1)

        for ci, (lbl, attr, default) in enumerate([
            ("GIÁ (đ)", "_price", p.price if p else ""),
            ("TỒN KHO", "_stock", p.stock if p else ""),
            ("CẢNH BÁO TỒN", "_min", p.minStockAlert if p else ""),
        ]):
            ctk.CTkLabel(row, text=lbl,
                         font=ctk.CTkFont(size=9, weight="bold"),
                         text_color=TEXT_MUTED).grid(row=0, column=ci, padx=(0, 8 if ci < 2 else 0), sticky="w")
            e = ctk.CTkEntry(row, height=40, corner_radius=8,
                              border_color=BORDER, border_width=1,
                              fg_color="#f8fafc", text_color=TEXT_PRIMARY,
                              font=ctk.CTkFont(size=12, weight="bold"))
            e.grid(row=1, column=ci, padx=(0, 8 if ci < 2 else 0), sticky="ew")
            if default != "":
                e.insert(0, str(default))
            setattr(self, attr, e)

        sep = ctk.CTkFrame(self, fg_color=BORDER, height=1, corner_radius=0)
        sep.pack(fill="x", pady=(20, 0))
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
            "name": self._name.get().strip(),
            "category": self._cat_var.get(),
            "price": self._price.get().strip(),
            "stock": self._stock.get().strip(),
            "minStockAlert": self._min.get().strip(),
        }
        if not data["name"]:
            return
        if self.product:
            data["__product__"] = self.product
        self.destroy()
        self.on_save(data)
