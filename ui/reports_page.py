"""
Báo cáo — Reports Page (dữ liệu thực từ DB)
"""
import csv
import matplotlib
import matplotlib.pyplot as plt
import customtkinter as ctk
from collections import defaultdict
from datetime import date
from ui.app import (ORANGE, ORANGE_LIGHT, ORANGE_DARK, WHITE, BG, TEXT_PRIMARY,
                     TEXT_SECONDARY, TEXT_MUTED, BORDER, EMERALD, RED, BLUE)

try:
    matplotlib.use("TkAgg")
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MPL = True
except ImportError:
    HAS_MPL = False


class TrangBaoCao(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, fg_color=BG, corner_radius=0, **kwargs)
        self.app = app
        self._canvas_list = []   # giữ tham chiếu tránh GC
        self._tao_giao_dien()

    def _lam_moi(self):
        """Gọi mỗi lần điều hướng tới báo cáo — rebuild toàn bộ với dữ liệu mới."""
        for c in self._canvas_list:
            try:
                plt.close()
                c.get_tk_widget().destroy()
            except Exception:
                pass
        self._canvas_list.clear()
        for w in self.winfo_children():
            w.destroy()
        self._tao_giao_dien()

    def _tao_giao_dien(self):
        self._canvas_list.clear()
        cuon = ctk.CTkScrollableFrame(self, fg_color=BG, corner_radius=0,
                                       scrollbar_button_color=BORDER)
        cuon.pack(fill="both", expand=True)

        # ─── Tiêu đề ───
        top = ctk.CTkFrame(cuon, fg_color=BG, corner_radius=0)
        top.pack(fill="x", padx=24, pady=(20, 4))
        ctk.CTkLabel(top, text="BÁO CÁO TỔNG HỢP",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(side="left")
        right_top = ctk.CTkFrame(top, fg_color=BG, corner_radius=0)
        right_top.pack(side="right")
        ctk.CTkLabel(right_top, text=f"Cập nhật: {date.today().strftime('%d/%m/%Y')}",
                     font=ctk.CTkFont(size=11), text_color=TEXT_MUTED).pack(side="right", padx=(16, 0))
        
        self.combo_xuat = ctk.CTkComboBox(right_top, values=["Theo tháng", "Theo năm"],
                                          width=120, height=36, corner_radius=8,
                                          border_color=BORDER, fg_color=WHITE, text_color=TEXT_PRIMARY)
        self.combo_xuat.pack(side="right", padx=(8, 0))
        
        ctk.CTkButton(right_top, text="📥 Xuất Báo Cáo", width=120, height=36,
                      fg_color=ORANGE, hover_color=ORANGE_DARK, text_color=WHITE,
                      font=ctk.CTkFont(weight="bold"), corner_radius=8,
                      command=self._xuat_bao_cao).pack(side="right")

        # ─── Lấy dữ liệu ───
        reports_data = self.app.du_lieu.get("reports", {})
        du_lieu_thang = reports_data.get("dt_theo_thang", [])
        thang = [x[0] for x in du_lieu_thang] if du_lieu_thang else []
        doanh_thu_thang = [x[1] for x in du_lieu_thang] if du_lieu_thang else []
        
        # ─── Tính KPIs ───
        tong_dt         = reports_data.get('tong_dt', 0.0)
        hv_active       = reports_data.get('hv_active', 0)
        hv_expired      = reports_data.get('hv_expired', 0)
        hv_pending      = reports_data.get('hv_pending', 0)
        su_kien_upcoming= reports_data.get('su_kien_upcoming', 0)
        tong_hoc_vien   = reports_data.get('tong_hoc_vien', 0)

        # Doanh thu tháng hiện tại
        dt_thang_nay = reports_data.get('dt_thang_nay', 0.0)

        # ─── KPI Cards ───
        kpis = [
            ("💰 Tổng doanh thu",   f"{tong_dt:,.0f} đ",     "Tích lũy toàn thời gian",  ORANGE,  "#fff7ed"),
            ("👥 Hội viên Active",  str(hv_active),            "Đang tập luyện",            EMERALD, "#ecfdf5"),
            ("📅 Sự kiện",          str(su_kien_upcoming),     "Sắp diễn ra",               BLUE,    "#eff6ff"),
            ("🎓 Học viên lớp",     str(tong_hoc_vien),        "Tổng đăng ký lớp học",      "#7c3aed","#f5f3ff"),
        ]
        hang_kpi = ctk.CTkFrame(cuon, fg_color=BG, corner_radius=0)
        hang_kpi.pack(fill="x", padx=24, pady=(0, 16))
        for ci, (ten, gia_tri, phu, mau, bg_c) in enumerate(kpis):
            hang_kpi.grid_columnconfigure(ci, weight=1)
            the = ctk.CTkFrame(hang_kpi, fg_color=WHITE, corner_radius=16,
                                border_width=1, border_color=BORDER)
            the.grid(row=0, column=ci, padx=(0, 12) if ci < 3 else 0, sticky="ew")
            ctk.CTkLabel(the, text=ten,
                         font=ctk.CTkFont(size=10, weight="bold"),
                         text_color=TEXT_MUTED).pack(anchor="w", padx=20, pady=(16, 0))
            ctk.CTkLabel(the, text=gia_tri,
                         font=ctk.CTkFont(size=26, weight="bold"),
                         text_color=mau).pack(anchor="w", padx=20)
            ctk.CTkLabel(the, text=phu,
                         font=ctk.CTkFont(size=10, weight="bold"),
                         text_color=TEXT_SECONDARY).pack(anchor="w", padx=20, pady=(0, 16))

        # ─── BIỂU ĐỒ DOANH THU THEO THÁNG ───
        if HAS_MPL and thang:
            the_bieu_do = ctk.CTkFrame(cuon, fg_color=WHITE, corner_radius=20,
                                       border_width=1, border_color=BORDER)
            the_bieu_do.pack(fill="x", padx=24, pady=(0, 16))

            dau = ctk.CTkFrame(the_bieu_do, fg_color=WHITE, corner_radius=0)
            dau.pack(fill="x", padx=24, pady=(16, 4))
            ctk.CTkLabel(dau, text="📊 Doanh Thu Theo Tháng",
                         font=ctk.CTkFont(size=14, weight="bold"),
                         text_color=TEXT_PRIMARY).pack(side="left")
            ctk.CTkLabel(dau, text=f"6 tháng gần nhất | Tổng: {tong_dt:,.0f} đ",
                         font=ctk.CTkFont(size=11), text_color=TEXT_MUTED).pack(side="right")

            fig, ax = plt.subplots(figsize=(10, 3.2), dpi=90)
            fig.patch.set_facecolor("#ffffff")
            ax.set_facecolor("#fafafa")
            colors = ["#fdba74" if m != thang[-1] else "#f97316" for m in thang]
            bars = ax.bar(thang, doanh_thu_thang, color=colors, alpha=0.9, width=0.55, zorder=2,
                          edgecolor="white", linewidth=1.5)
            ax.bar_label(bars,
                         labels=[f"{v/1e6:.1f}M" if v >= 1e6 else f"{v/1e3:.0f}K" for v in doanh_thu_thang],
                         fontsize=9, color="#64748b", padding=5, fontweight="bold")
            ax.set_ylim(0, max(doanh_thu_thang) * 1.35 if doanh_thu_thang else 1)
            ax.tick_params(axis="x", labelsize=10, labelcolor="#94a3b8")
            ax.tick_params(axis="y", labelsize=9,  labelcolor="#94a3b8")
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x/1e6:.1f}M" if x >= 1e6 else f"{x/1e3:.0f}K"))
            ax.grid(axis="y", color="#f1f5f9", linewidth=1.2, zorder=1)
            ax.spines[:].set_visible(False)
            fig.tight_layout(pad=1.5)

            canvas = FigureCanvasTkAgg(fig, master=the_bieu_do)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="x", padx=20, pady=(0, 16))
            plt.close(fig)
            self._canvas_list.append(canvas)

        # ─── HÀNG 2: Pie chart + Bảng hóa đơn ───
        hang2 = ctk.CTkFrame(cuon, fg_color=BG, corner_radius=0)
        hang2.pack(fill="x", padx=24, pady=(0, 16))
        hang2.grid_columnconfigure(0, weight=1)
        hang2.grid_columnconfigure(1, weight=2)

        # ── Pie: Tình trạng hội viên ──
        the_pie = ctk.CTkFrame(hang2, fg_color=WHITE, corner_radius=16,
                                border_width=1, border_color=BORDER)
        the_pie.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        ctk.CTkLabel(the_pie, text="👥 Tình Trạng Hội Viên",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=20, pady=(16, 4))

        if HAS_MPL and reports_data:
            dem = {
                "Hoạt động": hv_active,
                "Hết hạn": hv_expired,
                "Chờ duyệt": hv_pending
            }
            dem = {k: v for k, v in dem.items() if v > 0}
            fig2, ax2 = plt.subplots(figsize=(3.8, 3.2), dpi=90)
            fig2.patch.set_facecolor("#ffffff")
            maus = [EMERALD, RED, ORANGE][:len(dem)]
            wedges, texts, autotexts = ax2.pie(
                dem.values(), labels=dem.keys(), colors=maus,
                autopct="%1.0f%%", startangle=90, pctdistance=0.75,
                wedgeprops=dict(width=0.65, edgecolor="white", linewidth=2)
            )
            for t in texts:
                t.set_fontsize(10); t.set_color("#64748b")
            for at in autotexts:
                at.set_fontsize(10); at.set_fontweight("bold")
            ax2.text(0, 0, str(reports_data.get('tong_hoi_vien', 0)), ha="center", va="center",
                     fontsize=20, fontweight="bold", color=TEXT_PRIMARY)
            ax2.text(0, -0.3, "tổng", ha="center", va="center",
                     fontsize=9, color="#94a3b8")
            fig2.tight_layout(pad=0.5)
            canvas2 = FigureCanvasTkAgg(fig2, master=the_pie)
            canvas2.draw()
            canvas2.get_tk_widget().pack(fill="x", padx=12, pady=(0, 12))
            plt.close(fig2)
            self._canvas_list.append(canvas2)
        else:
            for label, count, color in [("Hoạt động", hv_active, EMERALD),
                                         ("Hết hạn", hv_expired, RED),
                                         ("Chờ duyệt", hv_pending, ORANGE)]:
                r = ctk.CTkFrame(the_pie, fg_color="#f8fafc", corner_radius=8)
                r.pack(fill="x", padx=12, pady=3)
                ctk.CTkLabel(r, text=label, font=ctk.CTkFont(size=11, weight="bold"),
                             text_color=color).pack(side="left", padx=12, pady=8)
                ctk.CTkLabel(r, text=str(count), font=ctk.CTkFont(size=14, weight="bold"),
                             text_color=TEXT_PRIMARY).pack(side="right", padx=12)

        # ── Bảng Top hóa đơn ──
        the_hd = ctk.CTkFrame(hang2, fg_color=WHITE, corner_radius=16,
                               border_width=1, border_color=BORDER)
        the_hd.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        dau_hd = ctk.CTkFrame(the_hd, fg_color=WHITE, corner_radius=0)
        dau_hd.pack(fill="x", padx=20, pady=(16, 8))
        ctk.CTkLabel(dau_hd, text="🧾 Hóa Đơn Gần Nhất",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(side="left")
        ctk.CTkLabel(dau_hd, text=f"Tổng: {reports_data.get('tong_hoa_don', 0)} hóa đơn",
                     font=ctk.CTkFont(size=11), text_color=TEXT_MUTED).pack(side="right")

        sorted_inv = reports_data.get('top_invoices', [])

        # ── Bảng dùng một grid duy nhất — header + data cùng cột ──
        bang = ctk.CTkFrame(the_hd, fg_color="transparent", corner_radius=0)
        bang.pack(fill="x", padx=12, pady=(0, 12))

        # Độ rộng từng cột (index 0-3)
        COL_W = [150, 90, 115, 110]
        COL_HDR = ["HỘI VIÊN", "NGÀY", "TỔNG TIỀN", "PHƯƠNG THỨC"]
        for ci, w in enumerate(COL_W):
            bang.grid_columnconfigure(ci, weight=1, minsize=w)

        # Header row
        hdr_bg = ctk.CTkFrame(bang, fg_color="#f8fafc", corner_radius=8, height=36)
        hdr_bg.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 2))
        hdr_bg.grid_propagate(False)
        hdr_inner = ctk.CTkFrame(hdr_bg, fg_color="transparent")
        hdr_inner.place(relx=0, rely=0, relwidth=1, relheight=1)
        for ci, (col, w) in enumerate(zip(COL_HDR, COL_W)):
            hdr_inner.grid_columnconfigure(ci, weight=1, minsize=w)
            ctk.CTkLabel(hdr_inner, text=col,
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=TEXT_MUTED, anchor="center").grid(
                row=0, column=ci, padx=4, pady=8, sticky="ew")

        _PT_VI = {"CASH": "Tiền mặt", "TRANSFER": "Chuyển khoản", "E-WALLET": "Ví điện tử"}
        _PT_COLOR = {"CASH": "#10b981", "TRANSFER": "#3b82f6", "E-WALLET": "#f97316",
                     "Tiền mặt": "#10b981", "Chuyển khoản": "#3b82f6", "Ví điện tử": "#f97316"}

        for ri, inv in enumerate(sorted_inv):
            ten_hv = inv['ten_hv']
            phuong_thuc = inv['phuong_thuc']
            phuong_thuc_hien = _PT_VI.get(phuong_thuc, phuong_thuc)
            mau_pt = _PT_COLOR.get(phuong_thuc, TEXT_MUTED)

            row_base = ri * 2 + 1   # hàng data (row 1, 3, 5...)
            sep_base = ri * 2 + 2   # hàng separator

            # Separator
            ctk.CTkFrame(bang, fg_color=BORDER, height=1, corner_radius=0).grid(
                row=sep_base, column=0, columnspan=4, sticky="ew")

            # Data cells
            ctk.CTkLabel(bang, text=ten_hv,
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=TEXT_PRIMARY, anchor="center").grid(
                row=row_base, column=0, padx=4, pady=(8, 12), sticky="w")
            ctk.CTkLabel(bang, text=inv['ngay'][:10], font=ctk.CTkFont(size=12),
                         text_color=TEXT_SECONDARY, anchor="center").grid(
                row=row_base, column=1, padx=4, pady=(8, 12))
            ctk.CTkLabel(bang, text=f"{inv['tong_tien']:,.0f} đ",
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=ORANGE, anchor="center").grid(
                row=row_base, column=2, padx=4, pady=(8, 12), sticky="e")
            ctk.CTkLabel(bang, text=phuong_thuc_hien,
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=mau_pt, anchor="center").grid(
                row=row_base, column=3, padx=4, pady=8, sticky="ew")

        # ─── HÀNG 3: Top sản phẩm + Lớp học ───
        hang3 = ctk.CTkFrame(cuon, fg_color=BG, corner_radius=0)
        hang3.pack(fill="x", padx=24, pady=(0, 24))
        hang3.grid_columnconfigure(0, weight=1)
        hang3.grid_columnconfigure(1, weight=1)

        # ── Top sản phẩm bán chạy ──
        the_sp = ctk.CTkFrame(hang3, fg_color=WHITE, corner_radius=16,
                               border_width=1, border_color=BORDER)
        the_sp.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        ctk.CTkLabel(the_sp, text="📦 Sản Phẩm Bán Chạy",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=20, pady=(16, 8))

        # Tính doanh số từ InvoiceItems (Đã lấy từ SQL)
        top_sp = reports_data.get('top_sp', [])
        max_rev = top_sp[0]['rev'] if top_sp else 1
        for sp in top_sp:
            ten = sp['ten']
            qty = sp['qty']
            rev = sp['rev']
            f = ctk.CTkFrame(the_sp, fg_color="transparent")
            f.pack(fill="x", padx=16, pady=3)
            ctk.CTkLabel(f, text=ten[:28], font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=TEXT_PRIMARY, anchor="w").pack(anchor="w")
            pb_frame = ctk.CTkFrame(f, fg_color="#f1f5f9", corner_radius=4, height=8)
            pb_frame.pack(fill="x", pady=(2, 0))
            ratio = rev / max_rev if max_rev > 0 else 0
            ctk.CTkFrame(pb_frame, fg_color=ORANGE, corner_radius=4,
                         height=8).place(relx=0, rely=0, relwidth=ratio)
            ctk.CTkLabel(f, text=f"SL: {qty}  |  {rev:,.0f} đ",
                         font=ctk.CTkFont(size=9), text_color=TEXT_MUTED).pack(anchor="w")

        # ── Tình trạng lớp học ──
        the_lop = ctk.CTkFrame(hang3, fg_color=WHITE, corner_radius=16,
                                border_width=1, border_color=BORDER)
        the_lop.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        ctk.CTkLabel(the_lop, text="🏋️ Tình Trạng Lớp Học",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=20, pady=(16, 8))

        tinh_trang_lop = reports_data.get('tinh_trang_lop', [])
        for lop in tinh_trang_lop:
            so_hv = lop['so_hv']
            suc_chua = lop['suc_chua']
            ratio = so_hv / suc_chua if suc_chua > 0 else 0
            mau_fill = RED if ratio >= 1.0 else (ORANGE if ratio >= 0.7 else EMERALD)
            ten_hlv = lop['hlv_name']

            f = ctk.CTkFrame(the_lop, fg_color="#f8fafc", corner_radius=10)
            f.pack(fill="x", padx=12, pady=4)

            top_row = ctk.CTkFrame(f, fg_color="transparent")
            top_row.pack(fill="x", padx=12, pady=(8, 2))
            ctk.CTkLabel(top_row, text=lop['ten'],
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=TEXT_PRIMARY).pack(side="left")
            ctk.CTkLabel(top_row, text=f"{so_hv}/{suc_chua} HV",
                         font=ctk.CTkFont(size=10, weight="bold"),
                         text_color=mau_fill).pack(side="right")

            pb_frame = ctk.CTkFrame(f, fg_color="#e2e8f0", corner_radius=4, height=6)
            pb_frame.pack(fill="x", padx=12, pady=(0, 2))
            ctk.CTkFrame(pb_frame, fg_color=mau_fill, corner_radius=4,
                         height=6).place(relx=0, rely=0, relwidth=min(ratio, 1.0))

            ctk.CTkLabel(f, text=f"HLV: {ten_hlv}",
                         font=ctk.CTkFont(size=10), text_color=TEXT_MUTED).pack(anchor="w", padx=12, pady=(2, 8))

    def _xuat_bao_cao(self):
        from tkinter import filedialog
        
        kieu_xuat = self.combo_xuat.get()
        invoices = self.app.du_lieu.get("invoices", [])
        
        dt_nhom = defaultdict(float)
        if kieu_xuat == "Theo tháng":
            for inv in invoices:
                if inv.ngay and len(inv.ngay) >= 7:
                    dt_nhom[inv.ngay[:7]] += inv.tong_tien
        else: # Theo năm
            for inv in invoices:
                if inv.ngay and len(inv.ngay) >= 4:
                    dt_nhom[inv.ngay[:4]] += inv.tong_tien
                    
        du_lieu_xuat = sorted(dt_nhom.items())
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Lưu file Báo Cáo"
        )
        if not file_path:
            return
            
        try:
            with open(file_path, mode="w", newline="", encoding="utf-8-sig") as file:
                writer = csv.writer(file)
                if kieu_xuat == "Theo tháng":
                    writer.writerow(["Tháng", "Tổng Doanh Thu (VND)"])
                else:
                    writer.writerow(["Năm", "Tổng Doanh Thu (VND)"])
                    
                for ky, tong in du_lieu_xuat:
                    writer.writerow([ky, tong])
            
            self.app.hien_thong_bao(f"Đã xuất báo cáo thành công!", "success")
        except Exception as e:
            self.app.hien_thong_bao(f"Lỗi khi xuất file: {e}", "error")
