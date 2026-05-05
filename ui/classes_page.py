"""
Quan ly Lop hoc — Classes Page
"""
import math
import services.class_service as cs_add
import services.class_service as cs_xoa
import threading
import customtkinter as ctk
import time
from models.models import BuoiHoc
import services.class_service as cs
from ui.app import (ORANGE, ORANGE_DARK, ORANGE_LIGHT, WHITE, BG,
                     TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, BORDER, EMERALD, RED, BLUE)


class TrangLopHoc(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, fg_color=BG, corner_radius=0, **kwargs)
        self.app = app
        self.trang_hien_tai = 1
        self.so_luong_moi_trang = 6
        self.bien_tim_kiem = ctk.StringVar()
        self.bien_tim_kiem.trace("w", lambda *a: self.app.debounce("class_search", self._lam_moi))
        self._tao_giao_dien()

    def _tao_giao_dien(self):
        top = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        top.pack(fill="x", padx=24, pady=(20, 0))

        ctk.CTkLabel(top, text="LỚP/BUỔI TẬP",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(side="left")

        vai_tro = self.app.nguoi_dung_hien_tai.vai_tro
        if vai_tro in ("ADMIN", "MANAGER"):
            ctk.CTkButton(top, text="＋  Tạo lớp mới",
                          font=ctk.CTkFont(size=11, weight="bold"),
                          fg_color=ORANGE, hover_color=ORANGE_DARK,
                          height=40, corner_radius=12,
                          command=self._mo_hop_thoai_them).pack(side="right")

        sf = ctk.CTkFrame(top, fg_color=WHITE, corner_radius=12,
                           border_width=1, border_color=BORDER)
        sf.pack(side="right", padx=(0, 12))
        ctk.CTkLabel(sf, text="🔍").pack(side="left", padx=(12, 0))
        ctk.CTkEntry(sf, textvariable=self.bien_tim_kiem,
                     placeholder_text="Tìm lớp học...",
                     width=200, height=38, border_width=0,
                     fg_color=WHITE, text_color=TEXT_PRIMARY,
                     font=ctk.CTkFont(size=12)).pack(side="left", padx=8)

        self.vung_cuon = ctk.CTkScrollableFrame(self, fg_color=BG, corner_radius=0,
                                               scrollbar_button_color=BORDER)
        self.vung_cuon.pack(fill="both", expand=True, padx=16, pady=16)

        # Pagination Bar
        self.khung_phan_trang = ctk.CTkFrame(self, fg_color=BG, height=60)
        self.khung_phan_trang.pack(fill="x", padx=24, pady=(0, 20))
        
        self.btn_truoc = ctk.CTkButton(self.khung_phan_trang, text="< Trước", width=80, height=32,
                                       fg_color=WHITE, text_color=TEXT_PRIMARY, border_width=1, border_color=BORDER,
                                       hover_color="#f1f5f9", command=self._trang_truoc)
        self.btn_truoc.pack(side="left")
        
        self.nhan_trang = ctk.CTkLabel(self.khung_phan_trang, text="Trang 1 / 1", font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT_MUTED)
        self.nhan_trang.pack(side="left", expand=True)
        
        self.btn_sau = ctk.CTkButton(self.khung_phan_trang, text="Sau >", width=80, height=32,
                                     fg_color=WHITE, text_color=TEXT_PRIMARY, border_width=1, border_color=BORDER,
                                     hover_color="#f1f5f9", command=self._trang_sau)
        self.btn_sau.pack(side="right")

        self._lam_moi()

    def _trang_truoc(self):
        if self.trang_hien_tai > 1:
            self.trang_hien_tai -= 1
            self._lam_moi()

    def _trang_sau(self):
        danh_sach = self.app.du_lieu["classes"]
        tong_so_trang = math.ceil(len(danh_sach) / self.so_luong_moi_trang)
        if self.trang_hien_tai < tong_so_trang:
            self.trang_hien_tai += 1
            self._lam_moi()

    def _lam_moi(self):
        for w in self.vung_cuon.winfo_children():
            w.destroy()
        tu_khoa = self.bien_tim_kiem.get().lower()
        danh_sach_lop = [c for c in self.app.du_lieu["classes"]
                   if not tu_khoa or tu_khoa in c.ten.lower()]
        
        tong_so_trang = math.ceil(len(danh_sach_lop) / self.so_luong_moi_trang) if danh_sach_lop else 1
        if self.trang_hien_tai > tong_so_trang: self.trang_hien_tai = tong_so_trang
        self.nhan_trang.configure(text=f"Trang {self.trang_hien_tai} / {tong_so_trang}")
        
        bat_dau = (self.trang_hien_tai - 1) * self.so_luong_moi_trang
        ket_thuc = bat_dau + self.so_luong_moi_trang
        hien_thi = danh_sach_lop[bat_dau:ket_thuc]

        if not hien_thi:
            ctk.CTkLabel(self.vung_cuon, text="Chưa có lớp học nào hoặc trang trống.",
                         font=ctk.CTkFont(size=13), text_color=TEXT_MUTED).pack(pady=60)
            return

        COLS = 3
        for col in range(COLS):
            self.vung_cuon.grid_columnconfigure(col, weight=1)
        for i, lop in enumerate(hien_thi):
            col = i % COLS
            row = i // COLS

            # Tìm HLV trong cả PT và MANAGER
            hlv = next((u for u in self.app.du_lieu["users"] if u.id == lop.id_hlv), None)
            ten_hlv = hlv.ho_ten if hlv else "Chưa phân công"
            so_luong = len(lop.danh_sach_id_hoi_vien)
            da_day = so_luong >= lop.suc_chua

            the = ctk.CTkFrame(self.vung_cuon, fg_color=WHITE, corner_radius=20,
                                 border_width=1, border_color=BORDER)
            the.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

            hdr = ctk.CTkFrame(the, fg_color=ORANGE if not da_day else "#f1f5f9",
                                corner_radius=12)
            hdr.pack(fill="x", padx=12, pady=(12, 0))
            ctk.CTkLabel(hdr, text=lop.ten.upper(),
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=WHITE if not da_day else TEXT_MUTED).pack(anchor="w", padx=16, pady=(12, 0))
            ctk.CTkLabel(hdr, text=f"🗓 {lop.thu_trong_tuan}  🕐 {lop.gio}",
                         font=ctk.CTkFont(size=11),
                         text_color=WHITE if not da_day else TEXT_SECONDARY).pack(anchor="w", padx=16, pady=(2, 12))

            chi_tiet = ctk.CTkFrame(the, fg_color="#f8fafc", corner_radius=12,
                                   border_width=1, border_color=BORDER)
            chi_tiet.pack(fill="x", padx=12, pady=8)
            du_lieu_dong = [
                ("🏋️ HLV", ten_hlv),
                ("👥 Học viên", f"{so_luong}/{lop.suc_chua}"),
                ("💰 Giá", f"{lop.gia:,.0f} đ" if getattr(lop, 'gia', 0) > 0 else "Miễn phí"),
                ("📊 Trạng thái", "Đầy" if da_day else "Còn chỗ"),
            ]
            chi_tiet.grid_columnconfigure(1, weight=1)
            for ri, (nhan, gia_tri) in enumerate(du_lieu_dong):
                ctk.CTkLabel(chi_tiet, text=nhan,
                             font=ctk.CTkFont(size=9, weight="bold"),
                             text_color=TEXT_MUTED).grid(row=ri, column=0, padx=12, pady=5, sticky="w")
                ctk.CTkLabel(chi_tiet, text=gia_tri,
                             font=ctk.CTkFont(size=11, weight="bold"),
                             text_color=RED if gia_tri == "Đầy" else TEXT_PRIMARY).grid(
                    row=ri, column=1, padx=12, pady=5, sticky="e")

            vai_tro = self.app.nguoi_dung_hien_tai.vai_tro
            if vai_tro in ("ADMIN", "MANAGER", "PT", "RECEPTIONIST"):
                hang_nut = ctk.CTkFrame(the, fg_color=WHITE, corner_radius=0)
                hang_nut.pack(fill="x", padx=12, pady=(0, 12))
                hang_nut.grid_columnconfigure((0, 1, 2), weight=1)
                
                ctk.CTkButton(hang_nut, text="Học viên", fg_color="#dbeafe", text_color=BLUE,
                              hover_color=BLUE, corner_radius=10, height=34,
                              font=ctk.CTkFont(size=11, weight="bold"),
                              command=lambda c=lop: self._hien_hoc_vien(c)).grid(
                    row=0, column=0, sticky="ew", padx=(0, 4))

                if vai_tro in ("ADMIN", "MANAGER"):
                    ctk.CTkButton(hang_nut, text="✏ Sửa",
                                  fg_color="#f1f5f9", text_color=TEXT_SECONDARY,
                                  hover_color="#dbeafe", corner_radius=10, height=34,
                                  font=ctk.CTkFont(size=11, weight="bold"),
                                  command=lambda c=lop: self._mo_hop_thoai_sua(c)).grid(
                        row=0, column=1, sticky="ew", padx=2)
                    ctk.CTkButton(hang_nut, text="🗑 Xóa",
                                  fg_color="#f1f5f9", text_color=TEXT_SECONDARY,
                                  hover_color="#fee2e2", corner_radius=10, height=34,
                                  font=ctk.CTkFont(size=11, weight="bold"),
                                  command=lambda c=lop: self._xac_nhan_xoa(c)).grid(
                        row=0, column=2, sticky="ew", padx=(4, 0))

    def _mo_hop_thoai_them(self):
        HopThoaiLopHoc(self, app=self.app, khi_luu=self._luu_them)

    def _mo_hop_thoai_sua(self, lop):
        HopThoaiLopHoc(self, app=self.app, buoi_hoc=lop, khi_luu=self._luu_sua)

    def _luu_them(self, du_lieu):
        try:
            suc_chua = int(du_lieu["suc_chua"]) if str(du_lieu["suc_chua"]).strip() else 20
        except ValueError:
            suc_chua = 20
        try:
            gia = float(du_lieu.get("gia", 0))
        except ValueError:
            gia = 0.0

        lop = BuoiHoc(
            id=str(int(time.time() * 1000)),
            ten=du_lieu["ten"], id_hlv=du_lieu["id_hlv"],
            gio=du_lieu["gio"], thu_trong_tuan=du_lieu["thu_trong_tuan"],
            suc_chua=suc_chua, gia=gia
        )
        def _worker():
            try:
                cs.them(lop)
            except Exception as e:
                self.after(0, lambda err=e: self.app.hien_thong_bao(f"Lỗi: {err}", "error"))
            else:
                def _ui():
                    self.app.du_lieu["classes"].append(lop)
                    self._lam_moi()
                    self.app.hien_thong_bao(f"Đã tạo lớp: {lop.ten}", "success")
                self.after(0, _ui)
        threading.Thread(target=_worker, daemon=True).start()

    def _luu_sua(self, du_lieu):
        lop = du_lieu["__buoi_hoc__"]
        lop.ten = du_lieu["ten"]
        lop.id_hlv = du_lieu["id_hlv"]
        lop.gio = du_lieu["gio"]
        lop.thu_trong_tuan = du_lieu["thu_trong_tuan"]
        try:
            lop.suc_chua = int(du_lieu["suc_chua"]) if str(du_lieu["suc_chua"]).strip() else lop.suc_chua
        except ValueError:
            pass
        try:
            lop.gia = float(du_lieu.get("gia", 0))
        except ValueError:
            pass
        def _worker():
            try:
                cs.cap_nhat(lop)
            except Exception as e:
                self.after(0, lambda err=e: self.app.hien_thong_bao(f"Lỗi: {err}", "error"))
            else:
                self.after(0, lambda: [
                    self._lam_moi(),
                    self.app.hien_thong_bao("Đã cập nhật lớp học", "success")
                ])
        threading.Thread(target=_worker, daemon=True).start()

    def _xac_nhan_xoa(self, lop):
        dlg = ctk.CTkToplevel(self)
        dlg.title("Xóa lớp học")
        w, h = 340, 190
        dlg.geometry(f"{w}x{h}")
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.configure(fg_color=WHITE)

        def _can_giua():


            x = (dlg.winfo_screenwidth() - w) // 2


            y = (dlg.winfo_screenheight() - h) // 2


            dlg.geometry(f"+{x}+{y}")
        dlg.after(10, _can_giua)

        ctk.CTkLabel(dlg, text="🗑  Xóa Lớp Học?",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(pady=(28, 4))
        ctk.CTkLabel(dlg, text=f"Lớp '{lop.ten}'\nsẽ bị xóa vĩnh viễn.",
                     font=ctk.CTkFont(size=11), text_color=TEXT_SECONDARY,
                     justify="center").pack(pady=(0, 20))
        hang = ctk.CTkFrame(dlg, fg_color=WHITE)
        hang.pack(fill="x", padx=24)
        ctk.CTkButton(hang, text="Hủy", fg_color="#f1f5f9", text_color=TEXT_SECONDARY,
                      hover_color=BORDER, font=ctk.CTkFont(weight="bold"),
                      command=dlg.destroy).pack(side="left", expand=True, fill="x", padx=(0, 6))
        ctk.CTkButton(hang, text="Xác nhận xóa", fg_color=RED, hover_color="#dc2626",
                      text_color=WHITE, font=ctk.CTkFont(weight="bold"),
                      command=lambda: self._thuc_hien_xoa(lop, dlg)).pack(
            side="left", expand=True, fill="x", padx=(6, 0))

    def _thuc_hien_xoa(self, lop, dlg):
        dlg.destroy()
        def _worker():
            try:
                cs.xoa(lop.id)
            except Exception as e:
                self.after(0, lambda err=e: self.app.hien_thong_bao(f"Lỗi: {err}", "error"))
            else:
                def _ui():
                    self.app.du_lieu["classes"] = [c for c in self.app.du_lieu["classes"] if c.id != lop.id]
                    self._lam_moi()
                    self.app.hien_thong_bao("Đã hủy lớp học", "success")
                self.after(0, _ui)
        threading.Thread(target=_worker, daemon=True).start()

    def _hien_hoc_vien(self, lop):
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Học viên: {lop.ten}")
        w, h = 680, 460
        dialog.geometry(f"{w}x{h}")
        dialog.resizable(False, True)
        dialog.grab_set()
        dialog.configure(fg_color=BG)

        def _can_giua():


            x = (dialog.winfo_screenwidth() - w) // 2


            y = (dialog.winfo_screenheight() - h) // 2


            dialog.geometry(f"+{x}+{y}")
        dialog.after(10, _can_giua)

        top = ctk.CTkFrame(dialog, fg_color=WHITE, corner_radius=0, height=56)
        top.pack(fill="x")
        top.pack_propagate(False)
        ctk.CTkLabel(top, text=f"👥  Học viên — {lop.ten}",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(side="left", padx=24, pady=16)

        ctk.CTkFrame(dialog, fg_color=BORDER, height=1, corner_radius=0).pack(fill="x")

        # Khung thêm người tham gia
        top_add = ctk.CTkFrame(dialog, fg_color=BG, corner_radius=0)
        top_add.pack(fill="x", padx=16, pady=(16, 0))
        
        all_members = self.app.du_lieu.get("members", [])
        map_hv = {m.id: m.ho_ten for m in all_members}
        danh_sach_hien_thi = [f"{m.id} - {m.ho_ten}" for m in all_members]

        combo_hv = ctk.CTkComboBox(top_add, values=danh_sach_hien_thi,
                                   width=350, height=36, corner_radius=8,
                                   border_color=BORDER, fg_color=WHITE, text_color=TEXT_PRIMARY)
        combo_hv.pack(side="left")
        
        def _them_tv():
            hien_tai = combo_hv.get()
            if not hien_tai or " - " not in hien_tai:
                return
            id_hv = hien_tai.split(" - ")[0]
            def _worker():
                try:
                    pass
                    result = cs_add.them_hoc_vien(lop.id, id_hv)
                    if result:
                        def _ui():
                            if id_hv not in lop.danh_sach_id_hoi_vien:
                                lop.danh_sach_id_hoi_vien.append(id_hv)
                            self.app.hien_thong_bao("Đã thêm học viên!", "success")
                            tai_ds()
                        self.after(0, _ui)
                    else:
                        self.after(0, lambda: self.app.hien_thong_bao(
                            "Học viên này đã ở trong lớp!", "error"))
                except Exception as e:
                    self.after(0, lambda err=e: self.app.hien_thong_bao(f"Lỗi: {err}", "error"))
            threading.Thread(target=_worker, daemon=True).start()

        ctk.CTkButton(top_add, text="Thêm học viên", width=120, height=36,
                      fg_color=ORANGE, hover_color=ORANGE_DARK, text_color=WHITE,
                      font=ctk.CTkFont(weight="bold"), corner_radius=8,
                      command=_them_tv).pack(side="left", padx=8)

        vung = ctk.CTkScrollableFrame(dialog, fg_color=BG,
                                      corner_radius=0, scrollbar_button_color=BORDER)
        vung.pack(fill="both", expand=True, padx=16, pady=16)

        def tai_ds():
            for c in vung.winfo_children():
                c.destroy()
            
            parts = lop.danh_sach_id_hoi_vien
            if not parts:
                ctk.CTkLabel(vung, text="Lớp chưa có học viên nào.",
                             text_color=TEXT_MUTED).pack(pady=30)
                return
            for p_id in parts:
                ten_hv = map_hv.get(p_id, f"Hội viên {p_id}")
                f = ctk.CTkFrame(vung, fg_color=WHITE, corner_radius=12,
                                 border_width=1, border_color=BORDER)
                f.pack(fill="x", pady=4)
                ctk.CTkLabel(f, text=ten_hv,
                             font=ctk.CTkFont(size=12, weight="bold"),
                             text_color=TEXT_PRIMARY).pack(side="left", padx=16, pady=12)
                
                ctk.CTkButton(f, text="Xóa", width=70, height=28,
                              fg_color="#fee2e2", text_color=RED,
                              hover_color=RED, corner_radius=8,
                              command=lambda pid=p_id: _xoa_thanh_vien(pid)).pack(
                    side="right", padx=(0, 16), pady=8)

        def _xoa_thanh_vien(pid):
            def _worker():
                try:
                    pass
                    cs_xoa.xoa_hoc_vien(lop.id, pid)
                    def _ui():
                        if pid in lop.danh_sach_id_hoi_vien:
                            lop.danh_sach_id_hoi_vien.remove(pid)
                        self.app.hien_thong_bao("Đã xóa học viên!", "success")
                        tai_ds()
                    self.after(0, _ui)
                except Exception as e:
                    self.after(0, lambda err=e: self.app.hien_thong_bao(f"Lỗi: {err}", "error"))
            threading.Thread(target=_worker, daemon=True).start()

        tai_ds()



class HopThoaiLopHoc(ctk.CTkToplevel):
    def __init__(self, master, app, khi_luu, buoi_hoc: BuoiHoc = None):
        super().__init__(master)
        self.title("Cập nhật lớp học" if buoi_hoc else "Tạo lớp học mới")
        w, h = 600, 540
        self.geometry(f"{w}x{h}")
        self.resizable(False, False)
        self.grab_set()
        self.configure(fg_color=WHITE)
        self.app = app
        self.buoi_hoc = buoi_hoc
        self.khi_luu = khi_luu

        def _can_giua():


            x = (self.winfo_screenwidth() - w) // 2


            y = (self.winfo_screenheight() - h) // 2


            self.geometry(f"+{x}+{y}")
        self.after(10, _can_giua)

        self._tao_giao_dien()

    def _tao_giao_dien(self):
        c = self.buoi_hoc
        tieu_de = "CẬP NHẬT LỚP HỌC" if c else "TẠO LỚP HỌC MỚI"



        # Footer
        chan = ctk.CTkFrame(self, fg_color=WHITE, height=72, corner_radius=0)
        chan.pack(side="bottom", fill="x")
        chan.pack_propagate(False)
        ctk.CTkFrame(self, fg_color=BORDER, height=1, corner_radius=0).pack(side="bottom", fill="x")

        # Body
        than = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=0)
        than.pack(side="top", fill="both", expand=True)

        def tao_o(cha, nhan, mac_dinh="", placeholder=""):
            ctk.CTkLabel(cha, text=nhan,
                         font=ctk.CTkFont(size=9, weight="bold"),
                         text_color=TEXT_MUTED, anchor="w").pack(fill="x", pady=(8, 2))
            o = ctk.CTkEntry(cha, height=44, corner_radius=10,
                             border_color=BORDER, border_width=1,
                             fg_color="#f8fafc", text_color=TEXT_PRIMARY,
                             font=ctk.CTkFont(size=13, weight="bold"),
                             placeholder_text=placeholder)
            o.pack(fill="x")
            if mac_dinh:
                o.insert(0, str(mac_dinh))
            return o

        # Row 1: Tên lớp & Ngày trong tuần
        hang1 = ctk.CTkFrame(than, fg_color="transparent")
        hang1.pack(fill="x", padx=16, pady=(12, 0))
        hang1.grid_columnconfigure((0, 1), weight=1)
        c1 = ctk.CTkFrame(hang1, fg_color="transparent")
        c1.grid(row=0, column=0, sticky="ew", padx=(8, 6))
        self._ten = tao_o(c1, "TÊN LỚP HỌC *", c.ten if c else "", "VD: Yoga sáng")
        c2 = ctk.CTkFrame(hang1, fg_color="transparent")
        c2.grid(row=0, column=1, sticky="ew", padx=(6, 8))
        self._thu = tao_o(c2, "NGÀY TRONG TUẦN", c.thu_trong_tuan if c else "", "Thứ 2, 4, 6")

        # Row 2: Giờ học & Sức chứa
        hang2 = ctk.CTkFrame(than, fg_color="transparent")
        hang2.pack(fill="x", padx=16)
        hang2.grid_columnconfigure((0, 1), weight=1)
        c3 = ctk.CTkFrame(hang2, fg_color="transparent")
        c3.grid(row=0, column=0, sticky="ew", padx=(8, 6))
        self._gio = tao_o(c3, "GIỜ HỌC", c.gio if c else "", "07:00")
        c4 = ctk.CTkFrame(hang2, fg_color="transparent")
        c4.grid(row=0, column=1, sticky="ew", padx=(6, 8))
        self._suc_chua = tao_o(c4, "SỨC CHỨA (người)", str(c.suc_chua) if c else "20", "20")

        # Row 3: Giá
        hang3 = ctk.CTkFrame(than, fg_color="transparent")
        hang3.pack(fill="x", padx=16)
        hang3.grid_columnconfigure((0, 1), weight=1)
        c5 = ctk.CTkFrame(hang3, fg_color="transparent")
        c5.grid(row=0, column=0, sticky="ew", padx=(8, 6))
        _gia_val = int(c.gia) if c and c.gia == int(c.gia) else (c.gia if c else 0)
        self._gia = tao_o(c5, "GIÁ (VND)", str(_gia_val) if c else "0", "0")

        # HLV: lấy tất cả PT và MANAGER
        ctk.CTkLabel(than, text="HUẤN LUYỆN VIÊN",
                     font=ctk.CTkFont(size=9, weight="bold"),
                     text_color=TEXT_MUTED, anchor="w").pack(fill="x", padx=24, pady=(12, 2))
        danh_sach_hlv = [u for u in self.app.du_lieu["users"]
                         if u.vai_tro in ("PT", "MANAGER")]
        ten_hlv_list = [t.ho_ten for t in danh_sach_hlv] or ["Chưa có HLV"]
        self._hlv_list = danh_sach_hlv
        self._combo_hlv = ctk.CTkComboBox(than, values=ten_hlv_list, height=44,
                                          corner_radius=10, border_color=BORDER,
                                          fg_color="#f8fafc", text_color=TEXT_PRIMARY,
                                          font=ctk.CTkFont(size=13, weight="bold"),
                                          button_color=ORANGE)
        self._combo_hlv.pack(fill="x", padx=24)
        if c:
            t = next((u for u in danh_sach_hlv if u.id == c.id_hlv), None)
            if t:
                self._combo_hlv.set(t.ho_ten)

        # Footer buttons
        chan.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(chan, text="Hủy", fg_color="#f1f5f9",
                      text_color=TEXT_SECONDARY, hover_color=BORDER,
                      font=ctk.CTkFont(weight="bold"), height=44, corner_radius=12,
                      command=self.destroy).grid(row=0, column=0, padx=(24, 6), pady=14, sticky="ew")
        ctk.CTkButton(chan, text="💾  Lưu lớp học", fg_color=ORANGE, hover_color=ORANGE_DARK,
                      text_color=WHITE, height=44, corner_radius=12,
                      font=ctk.CTkFont(weight="bold"),
                      command=self._gui).grid(row=0, column=1, padx=(6, 24), pady=14, sticky="ew")

    def _gui(self):
        from utils.validators import (khong_de_trong, dinh_dang_gio,
                                      la_so_nguyen_duong, kiem_tra_tat_ca)
        ten      = self._ten.get().strip()
        gio      = self._gio.get().strip()
        suc_chua = self._suc_chua.get().strip()
        gia      = self._gia.get().strip()
        ten_hlv  = self._combo_hlv.get()
        hlv      = next((u for u in self._hlv_list if u.ho_ten == ten_hlv), None)

        loi_list = kiem_tra_tat_ca([
            khong_de_trong(ten,  "Tên lớp học"),
            dinh_dang_gio(gio) if gio else None,
            la_so_nguyen_duong(suc_chua or "1", "Sức chứa") if suc_chua else None,
            None if hlv else "Vui lòng chọn Huấn luyện viên.",
        ])

        if gia:
            gia_clean = gia.replace(",", "")
            try:
                float(gia_clean)
            except ValueError:
                loi_list.append("Giá phải là một số hợp lệ.")

        if loi_list:
            try:
                frame = self.master
                while frame and not hasattr(frame, 'app'):
                    frame = getattr(frame, 'master', None)
                if frame and hasattr(frame, 'app'):
                    frame.app.hien_thong_bao("⚠ " + loi_list[0], "error")
            except Exception:
                pass
            return

        try:
            suc_chua_int = int(suc_chua) if suc_chua else 20
        except ValueError:
            suc_chua_int = 20

        try:
            gia_float = float(gia.replace(',', '')) if gia else 0.0
        except ValueError:
            gia_float = 0.0

        du_lieu = {
            "ten": ten,
            "gio": gio,
            "thu_trong_tuan": self._thu.get().strip(),
            "suc_chua": suc_chua_int,
            "gia": gia_float,
            "id_hlv": hlv.id if hlv else "",
        }
        if self.buoi_hoc:
            du_lieu["__buoi_hoc__"] = self.buoi_hoc
        self.destroy()
        self.khi_luu(du_lieu)

