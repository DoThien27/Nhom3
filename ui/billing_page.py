"""
Tai chinh / Billing Page - Ho tro Da dich vu
"""
import math
import threading
import time
from datetime import date
import customtkinter as ctk

from models.models import HoaDon, ChiTietHoaDon
import services.invoice_service as ivs
import services.plan_service as plan_srv
import services.class_service as class_srv
import services.facility_service as facility_srv
import services.event_service as event_srv

from ui.app import (ORANGE, ORANGE_DARK, ORANGE_LIGHT, WHITE, BG,
                     TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, BORDER, EMERALD, RED, BLUE)
from utils.formatters import (format_currency, parse_currency, format_date,
                              translate_payment_method, translate_payment_status,
                              PAYMENT_METHODS, PAYMENT_METHODS_VI, ITEM_TYPES, ITEM_TYPES_VI, translate_item_type)

class TrangTaiChinh(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, fg_color=BG, corner_radius=0, **kwargs)
        self.app = app
        self.trang_hien_tai = 1
        self.so_luong_moi_trang = 15
        self.bien_tim_kiem = ctk.StringVar()
        self.bien_tim_kiem.trace_add("write", lambda *a: self.app.debounce("billing_search", self._lam_moi_bang))
        
        self.combo_trang_thai = ctk.StringVar(value="Tất cả")
        
        self._tao_giao_dien()

    def _tao_giao_dien(self):
        # Top
        top = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        top.pack(fill="x", padx=24, pady=(20, 0))

        ctk.CTkLabel(top, text="TÀI CHÍNH & HÓA ĐƠN",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(side="left")

        ctk.CTkButton(top, text="＋  Tạo hóa đơn",
                       font=ctk.CTkFont(size=11, weight="bold"),
                       fg_color=ORANGE, hover_color=ORANGE_DARK,
                       height=40, corner_radius=12,
                       command=self._mo_hop_thoai_tao).pack(side="right")

        khung_tim_kiem = ctk.CTkFrame(top, fg_color=WHITE, corner_radius=12,
                                     border_width=1, border_color=BORDER)
        khung_tim_kiem.pack(side="right", padx=12)
        ctk.CTkLabel(khung_tim_kiem, text="🔍").pack(side="left", padx=(12, 0))
        ctk.CTkEntry(khung_tim_kiem, textvariable=self.bien_tim_kiem,
                     placeholder_text="Tìm hóa đơn/hội viên...",
                     width=200, height=38, border_width=0,
                     fg_color=WHITE, text_color=TEXT_PRIMARY,
                     font=ctk.CTkFont(size=12)).pack(side="left", padx=8)

        ctk.CTkOptionMenu(top, variable=self.combo_trang_thai,
                          values=["Tất cả", "Chưa thanh toán", "Thanh toán một phần", "Đã thanh toán", "Đã hủy"],
                          fg_color=WHITE, text_color=TEXT_PRIMARY, button_color=ORANGE,
                          button_hover_color=ORANGE_DARK, font=ctk.CTkFont(size=12),
                          command=lambda e: self._lam_moi_bang()).pack(side="right", padx=12)

        # Stats
        thong_ke = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        thong_ke.pack(fill="x", padx=24, pady=12)
        du_lieu_thong_ke = [
            ("💰 Doanh thu thu được", ORANGE),
            ("⚠️ Công nợ (Chưa thu)", RED),
            ("🧾 Số hóa đơn", BLUE),
        ]
        self._nhan_thong_ke = []
        for nhan, mau in du_lieu_thong_ke:
            the = ctk.CTkFrame(thong_ke, fg_color=WHITE, corner_radius=16,
                                 border_width=1, border_color=BORDER)
            the.pack(side="left", padx=(0, 12), ipadx=16, ipady=10)
            ctk.CTkLabel(the, text=nhan,
                         font=ctk.CTkFont(size=9, weight="bold"),
                         text_color=TEXT_MUTED).pack(anchor="w", padx=16, pady=(10, 0))
            lbl = ctk.CTkLabel(the, text="...",
                               font=ctk.CTkFont(size=18, weight="bold"),
                               text_color=mau)
            lbl.pack(anchor="w", padx=16, pady=(0, 10))
            self._nhan_thong_ke.append(lbl)

        # Table
        the_bang = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=20,
                                   border_width=1, border_color=BORDER)
        the_bang.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        the_bang.grid_rowconfigure(1, weight=1)
        the_bang.grid_columnconfigure(0, weight=1)

        # Table header
        cols = ["Mã HĐ", "Hội viên", "Ngày", "Tổng tiền", "Trạng thái", "Thao tác"]
        widths = [100, 160, 90, 130, 130, 80]
        hdr = ctk.CTkFrame(the_bang, fg_color="#f8fafc", corner_radius=0, border_width=0)
        hdr.grid(row=0, column=0, sticky="ew", padx=0)
        for ci, (col, w) in enumerate(zip(cols, widths)):
            ctk.CTkLabel(hdr, text=col.upper(),
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=TEXT_MUTED, width=w, anchor="center").grid(
                row=0, column=ci, padx=4, pady=10, sticky="ew")

        self.vung_cuon = ctk.CTkScrollableFrame(the_bang, fg_color=WHITE,
                                               corner_radius=0,
                                               scrollbar_button_color=BORDER)
        self.vung_cuon.grid(row=1, column=0, sticky="nsew")

        # Pagination Bar
        self.khung_phan_trang = ctk.CTkFrame(the_bang, fg_color="transparent", height=60)
        self.khung_phan_trang.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        
        self.btn_truoc = ctk.CTkButton(self.khung_phan_trang, text="< Trang trước", width=100, height=32,
                                       fg_color=WHITE, text_color=TEXT_PRIMARY, border_width=1, border_color=BORDER,
                                       hover_color="#f1f5f9", command=self._trang_truoc)
        self.btn_truoc.pack(side="left")
        
        self.nhan_trang = ctk.CTkLabel(self.khung_phan_trang, text="Trang 1 / 1", font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT_MUTED)
        self.nhan_trang.pack(side="left", expand=True)
        
        self.btn_sau = ctk.CTkButton(self.khung_phan_trang, text="Trang sau >", width=100, height=32,
                                     fg_color=WHITE, text_color=TEXT_PRIMARY, border_width=1, border_color=BORDER,
                                     hover_color="#f1f5f9", command=self._trang_sau)
        self.btn_sau.pack(side="right")

        self._tai_du_lieu_ban_dau()

    def _tai_du_lieu_ban_dau(self):
        def _worker():
            try:
                invoices = ivs.lay_tat_ca()
            except Exception as e:
                self.after(0, lambda: self.app.hien_thong_bao(f"Lỗi tải HD: {e}", "error"))
            else:
                def _ui():
                    self.app.du_lieu["invoices"] = invoices
                    self._cap_nhat_thong_ke()
                    self._lam_moi_bang()
                self.after(0, _ui)
        threading.Thread(target=_worker, daemon=True).start()

    def _trang_truoc(self):
        if self.trang_hien_tai > 1:
            self.trang_hien_tai -= 1
            self._lam_moi_bang()

    def _trang_sau(self):
        # We need to know total pages. We'll check logic in lam_moi_bang
        self.trang_hien_tai += 1
        self._lam_moi_bang()

    def _cap_nhat_thong_ke(self):
        if not hasattr(self, '_nhan_thong_ke') or len(self._nhan_thong_ke) < 3:
            return
        invoices = self.app.du_lieu.get("invoices", [])
        tong_da_thu = sum(i.da_tra for i in invoices if i.trang_thai_thanh_toan != "CANCELLED")
        tong_con_no = sum(i.con_lai for i in invoices if i.trang_thai_thanh_toan != "CANCELLED")
        so_luong = len([i for i in invoices if i.trang_thai_thanh_toan != "CANCELLED"])
        
        self._nhan_thong_ke[0].configure(text=format_currency(tong_da_thu))
        self._nhan_thong_ke[1].configure(text=format_currency(tong_con_no))
        self._nhan_thong_ke[2].configure(text=str(so_luong))

    def _lam_moi_bang(self):
        for w in self.vung_cuon.winfo_children():
            w.destroy()
            
        tu_khoa = self.bien_tim_kiem.get().lower()
        trang_thai_loc = self.combo_trang_thai.get()
        invoices = self.app.du_lieu.get("invoices", [])
        
        ket_qua = []
        for inv in invoices:
            ten_hv = getattr(inv, "_ten_hoi_vien", "") or inv.id_hoi_vien
            tt_vi = translate_payment_status(inv.trang_thai_thanh_toan)
            
            if tu_khoa and tu_khoa not in ten_hv.lower() and tu_khoa not in inv.id.lower():
                continue
            if trang_thai_loc != "Tất cả" and tt_vi != trang_thai_loc:
                continue
                
            ket_qua.append(inv)
            
        ket_qua.sort(key=lambda x: x.ngay, reverse=True)
        
        tong_so_trang = math.ceil(len(ket_qua) / self.so_luong_moi_trang) if ket_qua else 1
        if self.trang_hien_tai > tong_so_trang: self.trang_hien_tai = tong_so_trang
        
        self.nhan_trang.configure(text=f"Trang {self.trang_hien_tai} / {tong_so_trang}")
        
        bat_dau = (self.trang_hien_tai - 1) * self.so_luong_moi_trang
        ket_thuc = bat_dau + self.so_luong_moi_trang
        hien_thi = ket_qua[bat_dau:ket_thuc]

        from utils.formatters import PAYMENT_STATUS_COLORS

        widths = [100, 160, 90, 130, 130, 80]
        for inv in hien_thi:
            hang = ctk.CTkFrame(self.vung_cuon, fg_color=WHITE, corner_radius=0, border_width=0)
            hang.pack(fill="x")
            vach = ctk.CTkFrame(self.vung_cuon, fg_color=BORDER, height=1, corner_radius=0)
            vach.pack(fill="x")

            ten_hv = getattr(inv, "_ten_hoi_vien", "") or inv.id_hoi_vien
            tt_vi = translate_payment_status(inv.trang_thai_thanh_toan)
            mau_tt = PAYMENT_STATUS_COLORS.get(inv.trang_thai_thanh_toan, TEXT_PRIMARY)

            gia_tri = [
                inv.id[:10] + "...",
                ten_hv,
                format_date(inv.ngay),
                format_currency(inv.thanh_tien),
            ]
            
            for ci, (gt, w) in enumerate(zip(gia_tri, widths[:4])):
                lbl = ctk.CTkLabel(hang, text=gt, font=ctk.CTkFont(size=13),
                                   text_color=TEXT_PRIMARY, width=w, anchor="center")
                lbl.grid(row=0, column=ci, padx=4, pady=10, sticky="ew")
                
            # Trạng thái
            lbl_tt = ctk.CTkLabel(hang, text=tt_vi, font=ctk.CTkFont(size=12, weight="bold"),
                                  text_color=mau_tt, width=widths[4], anchor="center")
            lbl_tt.grid(row=0, column=4, padx=4, pady=10, sticky="ew")

            # Nút thao tác
            btn_frame = ctk.CTkFrame(hang, fg_color="transparent", width=widths[5])
            btn_frame.grid(row=0, column=5, padx=4, pady=10)
            
            btn_chi_tiet = ctk.CTkButton(btn_frame, text="Xem", width=50, height=24,
                                        fg_color="#f1f5f9", text_color=TEXT_SECONDARY, hover_color=BORDER,
                                        command=lambda i=inv: self._xem_chi_tiet(i))
            btn_chi_tiet.pack()

    def _xem_chi_tiet(self, invoice: HoaDon):
        # Dialog đơn giản hiển thị / hủy / trả thêm
        HopThoaiChiTietHoaDon(self, app=self.app, invoice=invoice, khi_cap_nhat=self._tai_du_lieu_ban_dau)

    def _mo_hop_thoai_tao(self):
        HopThoaiHoaDon(self, app=self.app, khi_luu=self._luu_hoa_don)

    def _luu_hoa_don(self, data):
        def _worker():
            try:
                # data = {id_hoi_vien, items, giam_gia_hd, da_tra, phuong_thuc, ghi_chu}
                id_hd = "INV" + str(int(time.time()))
                user_id = self.app.nguoi_dung_hien_tai.id if self.app.nguoi_dung_hien_tai else "SYSTEM"
                
                ivs.tao(
                    id_hoa_don=id_hd,
                    id_hoi_vien=data["id_hoi_vien"],
                    items=data["items"],
                    giam_gia_hd=data["giam_gia_hd"],
                    da_tra=data["da_tra"],
                    phuong_thuc=data["phuong_thuc"],
                    ghi_chu=data["ghi_chu"],
                    nguoi_tao=user_id
                )
            except Exception as e:
                self.after(0, lambda err=e: self.app.hien_thong_bao(f"Lỗi: {err}", "error"))
            else:
                self.after(0, lambda: self.app.hien_thong_bao("Đã tạo hóa đơn thành công", "success"))
                self.after(0, self._tai_du_lieu_ban_dau)
                
        threading.Thread(target=_worker, daemon=True).start()


class HopThoaiChiTietHoaDon(ctk.CTkToplevel):
    def __init__(self, master, app, invoice: HoaDon, khi_cap_nhat):
        super().__init__(master)
        self.title(f"Chi tiết hóa đơn {invoice.id}")
        self.geometry("600x500")
        self.resizable(False, False)
        self.grab_set()
        self.configure(fg_color=WHITE)
        self.app = app
        self.invoice = invoice
        self.khi_cap_nhat = khi_cap_nhat
        
        self.items = []
        self._tai_chi_tiet()

    def _tai_chi_tiet(self):
        def _worker():
            try:
                self.items = ivs.lay_cac_khoan(self.invoice.id)
            except Exception as e:
                pass
            else:
                self.after(0, self._tao_giao_dien)
        threading.Thread(target=_worker, daemon=True).start()
        
    def _tao_giao_dien(self):
        from utils.formatters import PAYMENT_STATUS_COLORS
        
        khung = ctk.CTkScrollableFrame(self, fg_color=WHITE)
        khung.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(khung, text=f"Hóa đơn: {self.invoice.id}", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(khung, text=f"Hội viên: {getattr(self.invoice, '_ten_hoi_vien', self.invoice.id_hoi_vien)}").pack(anchor="w")
        ctk.CTkLabel(khung, text=f"Ngày: {format_date(self.invoice.ngay)}").pack(anchor="w")
        
        tt_vi = translate_payment_status(self.invoice.trang_thai_thanh_toan)
        mau_tt = PAYMENT_STATUS_COLORS.get(self.invoice.trang_thai_thanh_toan, TEXT_PRIMARY)
        ctk.CTkLabel(khung, text=f"Trạng thái: {tt_vi}", text_color=mau_tt, font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 10))
        
        # Bảng chi tiết
        bang = ctk.CTkFrame(khung, fg_color="#f8fafc", corner_radius=8, border_color=BORDER, border_width=1)
        bang.pack(fill="x", pady=10)
        
        for it in self.items:
            h = ctk.CTkFrame(bang, fg_color="transparent")
            h.pack(fill="x", padx=10, pady=5)
            ctk.CTkLabel(h, text=f"[{translate_item_type(it.loai_khoan_thu)}] {it.ten}", font=ctk.CTkFont(weight="bold")).pack(side="left")
            ctk.CTkLabel(h, text=f"{it.so_luong} x {format_currency(it.gia)}").pack(side="right")
        
        # Tổng kết
        tk = ctk.CTkFrame(khung, fg_color="transparent")
        tk.pack(fill="x", pady=10)
        ctk.CTkLabel(tk, text=f"Tổng tiền: {format_currency(self.invoice.tong_tien)}").pack(anchor="e")
        ctk.CTkLabel(tk, text=f"Giảm giá: {format_currency(self.invoice.giam_gia)}").pack(anchor="e")
        ctk.CTkLabel(tk, text=f"Thành tiền: {format_currency(self.invoice.thanh_tien)}", font=ctk.CTkFont(weight="bold")).pack(anchor="e")
        
        # Nút hành động
        btn_frame = ctk.CTkFrame(self, fg_color=WHITE, height=60)
        btn_frame.pack(fill="x", side="bottom", padx=20, pady=10)
        
        if self.invoice.trang_thai_thanh_toan not in ["PAID", "CANCELLED"]:
            ctk.CTkButton(btn_frame, text="Thanh toán thêm", fg_color=EMERALD, hover_color="#047857",
                          command=self._thanh_toan_them).pack(side="right", padx=5)
            
        if self.invoice.trang_thai_thanh_toan != "CANCELLED" and self.invoice.trang_thai_thanh_toan != "PAID":
            ctk.CTkButton(btn_frame, text="Hủy hóa đơn", fg_color=RED, hover_color="#b91c1c",
                          command=self._huy_hoa_don).pack(side="left", padx=5)

    def _huy_hoa_don(self):
        # Dialog xác nhận
        # Giả lập xác nhận nhanh
        def _worker():
            try:
                ivs.huy(self.invoice.id)
            except Exception as e:
                self.after(0, lambda: self.app.hien_thong_bao(f"Lỗi: {e}", "error"))
            else:
                self.after(0, lambda: self.app.hien_thong_bao("Đã hủy hóa đơn", "success"))
                self.after(0, self.khi_cap_nhat)
                self.after(0, self.destroy)
        threading.Thread(target=_worker, daemon=True).start()

    def _thanh_toan_them(self):
        # Tạo dialog nhỏ yêu cầu nhập số tiền
        dialog = ctk.CTkInputDialog(text=f"Nhập số tiền trả thêm (Còn nợ: {format_currency(self.invoice.con_lai)}):", title="Thanh toán")
        val = dialog.get_input()
        if not val: return
        try:
            so_tien = parse_currency(val)
            if so_tien <= 0: return
        except ValueError:
            return
            
        def _worker():
            try:
                ivs.cap_nhat_thanh_toan(self.invoice.id, so_tien, phuong_thuc=self.invoice.phuong_thuc)
            except Exception as e:
                self.after(0, lambda: self.app.hien_thong_bao(f"Lỗi: {e}", "error"))
            else:
                self.after(0, lambda: self.app.hien_thong_bao("Đã cập nhật thanh toán", "success"))
                self.after(0, self.khi_cap_nhat)
                self.after(0, self.destroy)
        threading.Thread(target=_worker, daemon=True).start()


class HopThoaiHoaDon(ctk.CTkToplevel):
    def __init__(self, master, app, khi_luu):
        super().__init__(master)
        self.title("Tạo hóa đơn đa dịch vụ")
        w, h = 800, 750
        self.geometry(f"{w}x{h}")
        self.update_idletasks()
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"+{x}+{y}")
        self.resizable(False, True)
        self.grab_set()
        self.configure(fg_color=WHITE)
        self.app = app
        self.khi_luu = khi_luu
        
        self.danh_sach_muc: list[ChiTietHoaDon] = []
        self.service_options = {}
        
        self._khoi_tao_danh_sach()
        self._tao_giao_dien()
        
    def _khoi_tao_danh_sach(self):
        self.service_options.clear()
        
        # Membership
        for p in self.app.du_lieu.get("plans", []):
            label = f"{p.ten} - {format_currency(p.gia)}"
            self.service_options[label] = {
                "item_type": "MEMBERSHIP", "reference_id": p.id, "item_name": p.ten, "unit_price": p.gia
            }
            
        # Class
        for c in self.app.du_lieu.get("classes", []):
            gia = getattr(c, 'gia', 0)
            label = f"{c.ten} - {format_currency(gia)}" if gia else c.ten
            self.service_options[label] = {
                "item_type": "CLASS", "reference_id": c.id, "item_name": c.ten, "unit_price": gia
            }
            
        # Facility
        for f in self.app.du_lieu.get("facilities", []):
            gia = getattr(f, 'rental_price', getattr(f, 'default_price', 0))
            label = f"{f.ten} - {format_currency(gia)}" if gia else f.ten
            self.service_options[label] = {
                "item_type": "FACILITY", "reference_id": f.id, "item_name": f.ten, "unit_price": gia
            }
            
        # Event
        for e in self.app.du_lieu.get("events", []):
            gia = getattr(e, 'gia', 0)
            label = f"{e.ten} - {format_currency(gia)}" if gia else e.ten
            self.service_options[label] = {
                "item_type": "EVENT", "reference_id": e.id, "item_name": e.ten, "unit_price": gia
            }

    def _tao_giao_dien(self):
        chan_trang = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=0, height=72)
        chan_trang.pack(side="bottom", fill="x")
        chan_trang.pack_propagate(False)
        sep = ctk.CTkFrame(self, fg_color=BORDER, height=1, corner_radius=0)
        sep.pack(side="bottom", fill="x")
        self.chan_trang = chan_trang

        than = ctk.CTkScrollableFrame(self, fg_color=WHITE, corner_radius=0)
        than.pack(side="top", fill="both", expand=True)

        # Member
        ctk.CTkLabel(than, text="HỘI VIÊN *", font=ctk.CTkFont(size=9, weight="bold"), text_color=TEXT_MUTED).pack(anchor="w", padx=24, pady=(12, 2))
        ten_hoi_vien_list = [f"{m.id} - {m.ho_ten}" for m in self.app.du_lieu.get("members", [])]
        self.combo_hoi_vien = ctk.CTkComboBox(than, values=ten_hoi_vien_list, height=44, corner_radius=10, border_color=BORDER)
        self.combo_hoi_vien.pack(fill="x", padx=24)

        # Payment details
        khung_tt = ctk.CTkFrame(than, fg_color="transparent")
        khung_tt.pack(fill="x", padx=24, pady=10)
        
        ctk.CTkLabel(khung_tt, text="Phương thức:").grid(row=0, column=0, sticky="w", pady=5)
        self.bien_phuong_thuc = ctk.StringVar(value="Tiền mặt")
        self.combo_pt = ctk.CTkOptionMenu(khung_tt, variable=self.bien_phuong_thuc, values=PAYMENT_METHODS_VI)
        self.combo_pt.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        ctk.CTkLabel(khung_tt, text="Giảm giá HĐ (đ):").grid(row=1, column=0, sticky="w", pady=5)
        self.o_giam_gia_hd = ctk.CTkEntry(khung_tt, placeholder_text="0")
        self.o_giam_gia_hd.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        self.o_giam_gia_hd.bind("<KeyRelease>", self._tinh_lai_tong)
        self.o_giam_gia_hd.insert(0, "0")
        
        ctk.CTkLabel(khung_tt, text="Khách đã trả (đ):").grid(row=2, column=0, sticky="w", pady=5)
        self.o_da_tra = ctk.CTkEntry(khung_tt, placeholder_text="0")
        self.o_da_tra.grid(row=2, column=1, sticky="w", padx=10, pady=5)
        self.o_da_tra.bind("<KeyRelease>", self._tinh_lai_tong)
        self.o_da_tra.insert(0, "0")

        # Thêm Item
        ctk.CTkLabel(than, text="THÊM MỤC THANH TOÁN", font=ctk.CTkFont(size=9, weight="bold"), text_color=TEXT_MUTED).pack(anchor="w", padx=24, pady=(16, 4))
        
        hm = ctk.CTkFrame(than, fg_color="#f8fafc", corner_radius=8, border_width=1, border_color=BORDER)
        hm.pack(fill="x", padx=24)
        
        # Labels
        lbl_frame = ctk.CTkFrame(hm, fg_color="transparent")
        lbl_frame.pack(fill="x", padx=10, pady=(10, 0))
        lbl_frame.grid_columnconfigure(0, weight=1)
        lbl_frame.grid_columnconfigure(1, weight=2)
        lbl_frame.grid_columnconfigure(2, weight=1)
        lbl_frame.grid_columnconfigure(3, weight=1)
        lbl_frame.grid_columnconfigure(4, weight=0)
        
        ctk.CTkLabel(lbl_frame, text="Loại khoản thu", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=0, sticky="w", padx=4)
        ctk.CTkLabel(lbl_frame, text="Dịch vụ", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=1, sticky="w", padx=4)
        ctk.CTkLabel(lbl_frame, text="Số lượng", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=2, sticky="w", padx=4)
        ctk.CTkLabel(lbl_frame, text="Đơn giá", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=3, sticky="w", padx=4)
        ctk.CTkLabel(lbl_frame, text="Thao tác", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=4, sticky="w", padx=4)

        input_frame = ctk.CTkFrame(hm, fg_color="transparent")
        input_frame.pack(fill="x", padx=10, pady=(4, 10))
        input_frame.grid_columnconfigure(0, weight=1)
        input_frame.grid_columnconfigure(1, weight=2)
        input_frame.grid_columnconfigure(2, weight=1)
        input_frame.grid_columnconfigure(3, weight=1)
        input_frame.grid_columnconfigure(4, weight=0)
        
        self.combo_loai = ctk.CTkOptionMenu(input_frame, values=ITEM_TYPES_VI, command=self._doi_loai_muc)
        self.combo_loai.grid(row=0, column=0, padx=4, sticky="ew")
        
        self.combo_dich_vu = ctk.CTkComboBox(input_frame, values=[], command=self._chon_dich_vu)
        self.combo_dich_vu.grid(row=0, column=1, padx=4, sticky="ew")
        
        self.o_so_luong = ctk.CTkEntry(input_frame, placeholder_text="SL")
        self.o_so_luong.grid(row=0, column=2, padx=4, sticky="ew")
        self.o_so_luong.insert(0, "1")
        
        self.o_gia = ctk.CTkEntry(input_frame, placeholder_text="Đơn giá")
        self.o_gia.grid(row=0, column=3, padx=4, sticky="ew")
        
        ctk.CTkButton(input_frame, text="Thêm", width=60, fg_color=BLUE, hover_color="#1d4ed8", command=self._them_dong).grid(row=0, column=4, padx=4)
        
        # Trigger load lần đầu
        self._doi_loai_muc(ITEM_TYPES_VI[0])
        
        # Danh sách Items
        self.khung_cac_muc = ctk.CTkFrame(than, fg_color="transparent")
        self.khung_cac_muc.pack(fill="x", padx=24, pady=10)
        
        # Tổng hợp
        self.nhan_tong = ctk.CTkLabel(than, text="Tổng tiền: 0đ\nGiảm giá: 0đ\nThành tiền: 0đ\nCòn nợ: 0đ", 
                                      font=ctk.CTkFont(size=14, weight="bold"), justify="right")
        self.nhan_tong.pack(anchor="e", padx=24, pady=20)

        # Footer
        self.chan_trang.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(self.chan_trang, text="Hủy", fg_color="#f1f5f9", text_color=TEXT_SECONDARY, hover_color=BORDER,
                       command=self.destroy).grid(row=0, column=0, padx=(24, 6), pady=14, sticky="ew")
        ctk.CTkButton(self.chan_trang, text="Lưu hóa đơn", fg_color=ORANGE, hover_color=ORANGE_DARK, text_color=WHITE,
                       command=self._gui).grid(row=0, column=1, padx=(6, 24), pady=14, sticky="ew")

    def _doi_loai_muc(self, val_vi):
        loai_db = ITEM_TYPES[ITEM_TYPES_VI.index(val_vi)]
        
        if loai_db == "OTHER":
            self.combo_dich_vu.configure(values=["Nhập tay..."])
            self.combo_dich_vu.set("Nhập tay...")
            self.o_gia.delete(0, 'end')
            self.o_gia.configure(state="normal")
            return
            
        options = [k for k, v in self.service_options.items() if v["item_type"] == loai_db]
        
        if not options:
            self.combo_dich_vu.configure(values=["Không có dữ liệu, vui lòng nhập tay"])
            self.combo_dich_vu.set("Không có dữ liệu, vui lòng nhập tay")
            self.o_gia.delete(0, 'end')
            self.o_gia.configure(state="normal")
        else:
            self.combo_dich_vu.configure(values=options)
            self.combo_dich_vu.set(options[0])
            self._chon_dich_vu(options[0])

    def _chon_dich_vu(self, val):
        if val in self.service_options:
            info = self.service_options[val]
            self.o_gia.configure(state="normal")
            self.o_gia.delete(0, 'end')
            if info["unit_price"] > 0:
                self.o_gia.insert(0, str(int(info["unit_price"])))
        else:
            self.o_gia.configure(state="normal")
            self.o_gia.delete(0, 'end')

    def _them_dong(self):
        val_dich_vu = self.combo_dich_vu.get().strip()
        loai_vi = self.combo_loai.get()
        loai_db = ITEM_TYPES[ITEM_TYPES_VI.index(loai_vi)]
        
        if not val_dich_vu or val_dich_vu == "Không có dữ liệu, vui lòng nhập tay" or val_dich_vu == "Nhập tay...":
            self.app.hien_thong_bao("Vui lòng chọn hoặc nhập tên dịch vụ!", "error")
            return
            
        try:
            sl = int(self.o_so_luong.get())
            if sl <= 0: raise ValueError
        except:
            self.app.hien_thong_bao("Số lượng phải là số nguyên > 0", "error")
            return
            
        try:
            gia_str = self.o_gia.get()
            gia = parse_currency(gia_str) if gia_str else 0.0
            if gia < 0: raise ValueError
        except:
            self.app.hien_thong_bao("Đơn giá không hợp lệ", "error")
            return
            
        id_ref = None
        ten = val_dich_vu
        
        if val_dich_vu in self.service_options:
            info = self.service_options[val_dich_vu]
            id_ref = info["reference_id"]
            ten = info["item_name"]
            
        muc = ChiTietHoaDon(ten=ten, so_luong=sl, gia=gia, loai_khoan_thu=loai_db, id_tham_chieu=id_ref, giam_gia_dong=0)
        muc.thanh_tien = sl * gia
        self.danh_sach_muc.append(muc)
        self._lam_moi_danh_sach_muc()
        self._tinh_lai_tong()

    def _xoa_dong(self, idx):
        self.danh_sach_muc.pop(idx)
        self._lam_moi_danh_sach_muc()

    def _lam_moi_danh_sach_muc(self):
        for w in self.khung_cac_muc.winfo_children():
            w.destroy()
            
        for i, muc in enumerate(self.danh_sach_muc):
            tt = muc.so_luong * muc.gia
            h = ctk.CTkFrame(self.khung_cac_muc, fg_color="#f1f5f9", corner_radius=6)
            h.pack(fill="x", pady=2)
            ctk.CTkLabel(h, text=f"[{translate_item_type(muc.loai_khoan_thu)}] {muc.ten}", width=250, anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(h, text=f"{muc.so_luong} x {format_currency(muc.gia)} = {format_currency(tt)}", width=150, anchor="e").pack(side="left")
            ctk.CTkButton(h, text="X", width=30, fg_color=RED, command=lambda idx=i: self._xoa_dong(idx)).pack(side="right", padx=5)
            
        self._tinh_lai_tong()

    def _tinh_lai_tong(self, event=None):
        tong = sum(it.so_luong * it.gia for it in self.danh_sach_muc)
        giam = parse_currency(self.o_giam_gia_hd.get())
        thanh_tien = max(0, tong - giam)
        da_tra = parse_currency(self.o_da_tra.get())
        con_lai = max(0, thanh_tien - da_tra)
        
        self.nhan_tong.configure(text=f"Tổng tiền: {format_currency(tong)}\nGiảm giá: {format_currency(giam)}\nThành tiền: {format_currency(thanh_tien)}\nCòn nợ: {format_currency(con_lai)}")

    def _gui(self):
        if not self.danh_sach_muc:
            self.app.hien_thong_bao("Vui lòng thêm ít nhất một dịch vụ", "error")
            return
            
        hv_val = self.combo_hoi_vien.get()
        if not hv_val: return
        id_hv = hv_val.split(" - ")[0]
        
        pt_db = PAYMENT_METHODS[PAYMENT_METHODS_VI.index(self.bien_phuong_thuc.get())]
        giam = parse_currency(self.o_giam_gia_hd.get())
        da_tra = parse_currency(self.o_da_tra.get())
        
        du_lieu = {
            "id_hoi_vien": id_hv,
            "items": self.danh_sach_muc,
            "giam_gia_hd": giam,
            "da_tra": da_tra,
            "phuong_thuc": pt_db,
            "ghi_chu": ""
        }
        
        self.destroy()
        self.khi_luu(du_lieu)
