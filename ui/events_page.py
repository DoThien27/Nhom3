import math
import services.event_service as _evs
import services.member_service as _ms
import threading
import traceback
import customtkinter as ctk
import time

from ui.app import (ORANGE, ORANGE_DARK, ORANGE_LIGHT, WHITE, BG, TEXT_PRIMARY,
                     TEXT_SECONDARY, TEXT_MUTED, BORDER, EMERALD, RED, BLUE)
from models.models import SuKien
import services.event_service as evs


class TrangSuKien(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, fg_color=BG, corner_radius=0, **kwargs)
        self.app = app
        self.trang_hien_tai = 1
        self.so_luong_moi_trang = 10
        self._tao_bo_khung()
        self._tai_su_kien()

    def _tao_bo_khung(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Top Bar
        thanh_tren = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        thanh_tren.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 16))
        thanh_tren.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(thanh_tren, text="DANH SÁCH SỰ KIỆN",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=TEXT_PRIMARY).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(thanh_tren, text="＋  Thêm Sự Kiện",
                      font=ctk.CTkFont(size=11, weight="bold"),
                      fg_color=ORANGE, hover_color=ORANGE_DARK,
                      height=40, corner_radius=12,
                      command=self._hien_bieu_mau_su_kien).grid(row=0, column=2, sticky="e")

        # Main Content
        self.noi_dung_chinh = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=16,
                                         border_width=1, border_color=BORDER)
        self.noi_dung_chinh.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        self.noi_dung_chinh.grid_columnconfigure(0, weight=1)
        self.noi_dung_chinh.grid_rowconfigure(1, weight=1)

        # Header Row
        dau_muc = ctk.CTkFrame(self.noi_dung_chinh, fg_color="#f8fafc", corner_radius=0, height=48)
        dau_muc.grid(row=0, column=0, sticky="ew")
        dau_muc.grid_propagate(False)

        self._cols = ["TÊN SỰ KIỆN", "NGÀY/GIỜ", "ĐỊA ĐIỂM", "SỨC CHỨA", "GIÁ (VND)", "TRẠNG THÁI", "THAO TÁC"]
        self._widths = [240, 160, 180, 90, 130, 130, 180]

        for i, (text, w) in enumerate(zip(self._cols, self._widths)):
            ctk.CTkLabel(dau_muc, text=text,
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=TEXT_MUTED, width=w, anchor="center").pack(side="left", padx=4, pady=12)

        # List Frame
        self.vung_danh_sach = ctk.CTkScrollableFrame(
            self.noi_dung_chinh, fg_color="transparent", corner_radius=0,
            scrollbar_button_color=BORDER)
        self.vung_danh_sach.grid(row=1, column=0, sticky="nsew")

        # Pagination Bar
        self.khung_phan_trang = ctk.CTkFrame(self.noi_dung_chinh, fg_color="transparent", height=60)
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

    def _trang_truoc(self):
        if self.trang_hien_tai > 1:
            self.trang_hien_tai -= 1
            self._ve_danh_sach()

    def _trang_sau(self):
        danh_sach = self.app.du_lieu.get("events", [])
        tong_so_trang = math.ceil(len(danh_sach) / self.so_luong_moi_trang)
        if self.trang_hien_tai < tong_so_trang:
            self.trang_hien_tai += 1
            self._ve_danh_sach()

    def _tai_su_kien(self):
        for w in self.vung_danh_sach.winfo_children():
            w.destroy()

        danh_sach = self.app.du_lieu.get("events", [])
        def _load():
            try:
                data = evs.lay_tat_ca_su_kien()
                self.app.du_lieu["events"] = data
                # Cập nhật UI trên main thread
                self.after(0, self._ve_danh_sach)
            except Exception:
                self.after(0, self._ve_danh_sach)
        # Vẽ danh sách hiện tại ngay (tránh trắng trang), sau đó load mới
        self._ve_danh_sach()
        threading.Thread(target=_load, daemon=True).start()

    def _ve_danh_sach(self):
        for w in self.vung_danh_sach.winfo_children():
            w.destroy()

        danh_sach = self.app.du_lieu.get("events", [])
        
        tong_so_trang = math.ceil(len(danh_sach) / self.so_luong_moi_trang) if danh_sach else 1
        if self.trang_hien_tai > tong_so_trang: self.trang_hien_tai = tong_so_trang
        
        self.nhan_trang.configure(text=f"Trang {self.trang_hien_tai} / {tong_so_trang}")
        
        bat_dau = (self.trang_hien_tai - 1) * self.so_luong_moi_trang
        ket_thuc = bat_dau + self.so_luong_moi_trang
        hien_thi = danh_sach[bat_dau:ket_thuc]

        if not hien_thi:
            ctk.CTkLabel(self.vung_danh_sach, text="Chưa có sự kiện nào hoặc trang trống.",
                         font=ctk.CTkFont(size=13), text_color=TEXT_MUTED).pack(pady=40)
            return

        for idx, sk in enumerate(hien_thi):
            # Separator
            if idx > 0:
                sep = ctk.CTkFrame(self.vung_danh_sach, fg_color=BORDER, height=1, corner_radius=0)
                sep.pack(fill="x")

            khung_hang = ctk.CTkFrame(self.vung_danh_sach, fg_color="transparent", corner_radius=0)
            khung_hang.pack(fill="x", pady=0)

            ctk.CTkLabel(khung_hang, text=sk.ten, width=self._widths[0],
                         font=ctk.CTkFont(size=14, weight="bold"),
                         text_color=TEXT_PRIMARY, anchor="center").pack(side="left", padx=4, pady=14)

            ctk.CTkLabel(khung_hang, text=f"{sk.ngay}  {sk.gio}", width=self._widths[1],
                         font=ctk.CTkFont(size=14), text_color=TEXT_SECONDARY, anchor="center").pack(side="left", padx=4, pady=14)

            ctk.CTkLabel(khung_hang, text=sk.dia_diem, width=self._widths[2],
                         font=ctk.CTkFont(size=14), text_color=TEXT_SECONDARY, anchor="center").pack(side="left", padx=4, pady=14)

            ctk.CTkLabel(khung_hang, text=str(sk.suc_chua), width=self._widths[3],
                         font=ctk.CTkFont(size=14, weight="bold"), text_color=ORANGE, anchor="center").pack(side="left", padx=4, pady=14)

            ctk.CTkLabel(khung_hang, text=f"{sk.gia:,.0f}", width=self._widths[4],
                         font=ctk.CTkFont(size=14, weight="bold"), text_color=TEXT_PRIMARY, anchor="center").pack(side="left", padx=4, pady=14)

            _TT_SK = {"UPCOMING": "Sắp diễn ra", "ONGOING": "Đang diễn ra", "COMPLETED": "Đã kết thúc", "CANCELLED": "Đã hủy"}
            ten_tt = _TT_SK.get(sk.trang_thai, sk.trang_thai)
            mau = EMERALD if sk.trang_thai == "UPCOMING" else (
                BLUE if sk.trang_thai == "ONGOING" else (
                TEXT_SECONDARY if sk.trang_thai == "COMPLETED" else RED))
            ctk.CTkLabel(khung_hang, text=ten_tt, width=self._widths[5],
                         font=ctk.CTkFont(size=14, weight="bold"), text_color=mau, anchor="center").pack(side="left", padx=4, pady=14)

            khung_nut = ctk.CTkFrame(khung_hang, fg_color="transparent")
            khung_nut.pack(side="left", padx=8, pady=8)
            ctk.CTkButton(khung_nut, text="Người", width=56, height=28,
                          font=ctk.CTkFont(size=10, weight="bold"),
                          fg_color="#dbeafe", text_color=BLUE, hover_color=BLUE,
                          corner_radius=8,
                          command=lambda e=sk: self._hien_nguoi_tham_gia(e)).pack(side="left", padx=2)
            ctk.CTkButton(khung_nut, text="Sửa", width=46, height=28,
                          font=ctk.CTkFont(size=10, weight="bold"),
                          fg_color="#f1f5f9", text_color=TEXT_SECONDARY,
                          hover_color="#dbeafe", corner_radius=8,
                          command=lambda e=sk: self._hien_bieu_mau_su_kien(e)).pack(side="left", padx=2)
            ctk.CTkButton(khung_nut, text="Xóa", width=46, height=28,
                          font=ctk.CTkFont(size=10, weight="bold"),
                          fg_color="#f1f5f9", text_color=TEXT_SECONDARY,
                          hover_color="#fee2e2", corner_radius=8,
                          command=lambda e=sk: self._xac_nhan_xoa(e)).pack(side="left", padx=2)

    # ------------------------------------------------------------------
    def _hien_bieu_mau_su_kien(self, su_kien=None):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Cập nhật Sự Kiện" if su_kien else "Thêm Sự Kiện Mới")
        w, h = 600, 560
        dialog.geometry(f"{w}x{h}")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.configure(fg_color=WHITE)

        def _can_giua():


            x = (dialog.winfo_screenwidth() - w) // 2


            y = (dialog.winfo_screenheight() - h) // 2


            dialog.geometry(f"+{x}+{y}")
        dialog.after(10, _can_giua)



        # Footer
        chan = ctk.CTkFrame(dialog, fg_color=WHITE, height=72, corner_radius=0)
        chan.pack(side="bottom", fill="x")
        chan.pack_propagate(False)
        ctk.CTkFrame(dialog, fg_color=BORDER, height=1, corner_radius=0).pack(side="bottom", fill="x")

        # Body
        than = ctk.CTkFrame(dialog, fg_color=WHITE, corner_radius=0)
        than.pack(side="top", fill="both", expand=True)

        entries = {}

        def tao_o(cha, nhan, key, placeholder=""):
            ctk.CTkLabel(cha, text=nhan,
                         font=ctk.CTkFont(size=9, weight="bold"),
                         text_color=TEXT_MUTED, anchor="w").pack(fill="x", pady=(8, 2))
            o = ctk.CTkEntry(cha, height=40, corner_radius=10,
                             border_color=BORDER, border_width=1,
                             fg_color="#f8fafc", text_color=TEXT_PRIMARY,
                             font=ctk.CTkFont(size=12, weight="bold"),
                             placeholder_text=placeholder)
            o.pack(fill="x")
            if su_kien and hasattr(su_kien, key):
                val = getattr(su_kien, key)
                if val is not None:
                    # Format float đẹp: 50000.0 -> "50000"
                    if isinstance(val, float) and val == int(val):
                        val = int(val)
                    o.insert(0, str(val))
            entries[key] = o

        # Row 1: Tên & Mô tả
        hang1 = ctk.CTkFrame(than, fg_color="transparent")
        hang1.pack(fill="x", padx=20, pady=(8, 0))
        hang1.grid_columnconfigure((0, 1), weight=1)
        c1 = ctk.CTkFrame(hang1, fg_color="transparent")
        c1.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        tao_o(c1, "TÊN SỰ KIỆN *", "ten")
        c2 = ctk.CTkFrame(hang1, fg_color="transparent")
        c2.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        tao_o(c2, "MÔ TẢ", "mo_ta")

        # Row 2: Ngày & Giờ
        hang2 = ctk.CTkFrame(than, fg_color="transparent")
        hang2.pack(fill="x", padx=20)
        hang2.grid_columnconfigure((0, 1), weight=1)
        c3 = ctk.CTkFrame(hang2, fg_color="transparent")
        c3.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        tao_o(c3, "NGÀY (YYYY-MM-DD) *", "ngay", "2024-12-31")
        c4 = ctk.CTkFrame(hang2, fg_color="transparent")
        c4.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        tao_o(c4, "GIỜ (HH:MM) *", "gio", "08:00")

        # Row 3: Địa điểm & Sức chứa
        hang3 = ctk.CTkFrame(than, fg_color="transparent")
        hang3.pack(fill="x", padx=20)
        hang3.grid_columnconfigure((0, 1), weight=1)
        c5 = ctk.CTkFrame(hang3, fg_color="transparent")
        c5.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        tao_o(c5, "ĐỊA ĐIỂM *", "dia_diem", "Phòng A")
        c6 = ctk.CTkFrame(hang3, fg_color="transparent")
        c6.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        tao_o(c6, "SỨC CHỨA", "suc_chua", "50")

        # Row 4: Giá
        hang4 = ctk.CTkFrame(than, fg_color="transparent")
        hang4.pack(fill="x", padx=20)
        hang4.grid_columnconfigure((0, 1), weight=1)
        c7 = ctk.CTkFrame(hang4, fg_color="transparent")
        c7.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        tao_o(c7, "GIÁ (VND)", "gia", "0")

        # Trạng thái (chỉ khi sửa)
        trang_thai_var = ctk.StringVar(value=su_kien.trang_thai if su_kien else "UPCOMING")
        _TT_HIEN = {"UPCOMING": "Sắp diễn ra", "ONGOING": "Đang diễn ra", "COMPLETED": "Đã kết thúc", "CANCELLED": "Đã hủy"}
        _TT_DB = {v: k for k, v in _TT_HIEN.items()}  # reverse map
        if su_kien:
            ctk.CTkLabel(than, text="TRẠNG THÁI",
                         font=ctk.CTkFont(size=9, weight="bold"),
                         text_color=TEXT_MUTED, anchor="w").pack(fill="x", padx=24, pady=(8, 2))
            _bien_hien = ctk.StringVar(value=_TT_HIEN.get(su_kien.trang_thai, su_kien.trang_thai))
            cb = ctk.CTkComboBox(than,
                                 values=list(_TT_HIEN.values()),
                                 variable=_bien_hien,
                                 height=40, corner_radius=10,
                                 border_color=BORDER, fg_color="#f8fafc",
                                 text_color=TEXT_PRIMARY,
                                 font=ctk.CTkFont(size=12, weight="bold"),
                                 button_color=ORANGE)
            cb.pack(fill="x", padx=24)
            # Map display value back to DB value for saving
            def _sync_tt(*_):
                trang_thai_var.set(_TT_DB.get(_bien_hien.get(), _bien_hien.get()))
            _bien_hien.trace("w", _sync_tt)
            _sync_tt()

        # Footer buttons
        chan.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(chan, text="Hủy", fg_color="#f1f5f9",
                      text_color=TEXT_SECONDARY, hover_color=BORDER,
                      font=ctk.CTkFont(weight="bold"), height=44, corner_radius=12,
                      command=dialog.destroy).grid(row=0, column=0, padx=(24, 6), pady=14, sticky="ew")

        def _luu():
            from utils.validators import (khong_de_trong, dinh_dang_ngay,
                                          dinh_dang_gio, la_so_nguyen_duong,
                                          kiem_tra_tat_ca)
            ten      = entries["ten"].get().strip()
            ngay     = entries["ngay"].get().strip()
            gio      = entries["gio"].get().strip()
            dia_diem = entries["dia_diem"].get().strip()
            suc_chua = entries["suc_chua"].get().strip()
            gia      = entries.get("gia").get().strip() if "gia" in entries else "0"

            loi_list = kiem_tra_tat_ca([
                khong_de_trong(ten,      "Tên sự kiện"),
                khong_de_trong(dia_diem, "Địa điểm"),
                dinh_dang_ngay(ngay),
                dinh_dang_gio(gio),
                la_so_nguyen_duong(suc_chua or "1", "Sức chứa") if suc_chua else None,
            ])
            if loi_list:
                self.app.hien_thong_bao("⚠ " + loi_list[0], "error")
                return

            try:
                suc_chua_int = int(suc_chua) if suc_chua else 0
            except ValueError:
                suc_chua_int = 0
            try:
                gia_float = float(gia) if gia else 0.0
            except ValueError:
                gia_float = 0.0

            sk = SuKien(
                id=str(int(time.time() * 1000)) if not su_kien else su_kien.id,
                ten=ten, mo_ta=entries["mo_ta"].get().strip(),
                ngay=ngay, gio=gio, dia_diem=dia_diem,
                suc_chua=suc_chua_int, gia=gia_float, trang_thai=trang_thai_var.get()
            )

            # Vô hiệu hóa nút lưu trong lúc đang xử lý
            nut_luu.configure(state="disabled", text="Đang lưu...")

            def _worker():
                try:
                    if su_kien:
                        evs.cap_nhat_su_kien(sk)
                    else:
                        evs.them_su_kien(sk)
                    # Load lại danh sách mới từ DB
                    data = evs.lay_tat_ca_su_kien()
                    def _cap_nhat_ui():
                        self.app.du_lieu["events"] = data
                        self._ve_danh_sach()
                        self.app.hien_thong_bao("Đã lưu sự kiện thành công!", "success")
                        try:
                            dialog.destroy()
                        except Exception:
                            pass
                    self.after(0, _cap_nhat_ui)
                except Exception as e:
                    def _hien_loi(err=e):
                        self.app.hien_thong_bao(f"Lỗi: {err}", "error")
                        try:
                            nut_luu.configure(state="normal", text="💾  Lưu")
                        except Exception:
                            pass
                    self.after(0, _hien_loi)
            threading.Thread(target=_worker, daemon=True).start()

        nut_luu = ctk.CTkButton(chan, text="💾  Lưu", fg_color=ORANGE, hover_color=ORANGE_DARK)
        nut_luu.configure(
            text_color=WHITE, font=ctk.CTkFont(weight="bold"),
            height=44, corner_radius=12,
            command=_luu)
        nut_luu.grid(row=0, column=1, padx=(6, 24), pady=14, sticky="ew")

    def _xac_nhan_xoa(self, su_kien):
        dlg = ctk.CTkToplevel(self)
        dlg.title("Xác nhận xóa")
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

        ctk.CTkLabel(dlg, text="🗑  Xóa Sự Kiện?",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(pady=(28, 4))
        ctk.CTkLabel(dlg, text=f"Sự kiện \"{su_kien.ten}\"\nsẽ bị xóa vĩnh viễn.",
                     font=ctk.CTkFont(size=11), text_color=TEXT_SECONDARY,
                     justify="center").pack(pady=(0, 20))
        hang = ctk.CTkFrame(dlg, fg_color=WHITE)
        hang.pack(fill="x", padx=24)
        ctk.CTkButton(hang, text="Hủy", fg_color="#f1f5f9", text_color=TEXT_SECONDARY,
                      hover_color=BORDER, font=ctk.CTkFont(weight="bold"),
                      command=dlg.destroy).pack(side="left", expand=True, fill="x", padx=(0, 6))
        ctk.CTkButton(hang, text="Xác nhận xóa", fg_color=RED, hover_color="#dc2626",
                      text_color=WHITE, font=ctk.CTkFont(weight="bold"),
                      command=lambda: self._thuc_hien_xoa(su_kien, dlg)).pack(
            side="left", expand=True, fill="x", padx=(6, 0))

    def _thuc_hien_xoa(self, su_kien, dlg):
        dlg.destroy()
        try:
            evs.xoa_su_kien(su_kien.id)
            self.app.du_lieu["events"] = [e for e in self.app.du_lieu.get("events", []) if e.id != su_kien.id]
            self._ve_danh_sach()
            self.app.hien_thong_bao("Đã xóa sự kiện!", "success")
        except Exception as e:
            self.app.hien_thong_bao(f"Lỗi: {e}", "error")

    def _hien_nguoi_tham_gia(self, su_kien):
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Người tham gia: {su_kien.ten}")
        w, h = 720, 520
        dialog.geometry(f"{w}x{h}")
        dialog.resizable(False, True)
        dialog.grab_set()
        dialog.configure(fg_color=BG)

        def _can_giua():


            x = (dialog.winfo_screenwidth() - w) // 2


            y = (dialog.winfo_screenheight() - h) // 2


            dialog.geometry(f"+{x}+{y}")
        dialog.after(10, _can_giua)

        # Header
        top = ctk.CTkFrame(dialog, fg_color=WHITE, corner_radius=0, height=56)
        top.pack(fill="x")
        top.pack_propagate(False)
        ctk.CTkLabel(top, text=f"👥  Người Tham Gia — {su_kien.ten}",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(side="left", padx=24, pady=16)
        ctk.CTkFrame(dialog, fg_color=BORDER, height=1, corner_radius=0).pack(fill="x")

        # Thanh thêm người
        top_add = ctk.CTkFrame(dialog, fg_color=WHITE, corner_radius=0)
        top_add.pack(fill="x", padx=16, pady=10)
        ctk.CTkLabel(top_add, text="Chọn hội viên:",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=TEXT_SECONDARY).pack(side="left", padx=(4, 8))

        # Load danh sách hội viên đồng bộ mỗi khi mở form để đảm bảo dữ liệu mới nhất
        try:
            pass
            all_members = _ms.lay_tat_ca()
            # Cập nhật lại cache nếu cần
            self.app.du_lieu["members"] = all_members
        except Exception as e:
            print(f"[events_page] Lỗi tải danh sách hội viên: {e}")
            traceback.print_exc()
            all_members = self.app.du_lieu.get("members", []) # Fallback về cache cũ nếu lỗi DB

        _map_hv = {m.id: m.ho_ten for m in all_members}
        _ds_hv = [f"{m.id} - {m.ho_ten}" for m in all_members]

        combo_hv = ctk.CTkComboBox(
            top_add,
            values=_ds_hv if _ds_hv else ["-- Không có hội viên --"],
            width=360, height=36, corner_radius=8,
            border_color=BORDER, fg_color="#f8fafc", text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(size=12),
        )
        combo_hv.pack(side="left")
        if _ds_hv:
            combo_hv.set(_ds_hv[0])

        btn_them = ctk.CTkButton(
            top_add, text="＋  Thêm", width=100, height=36,
            fg_color=ORANGE, hover_color=ORANGE_DARK, text_color=WHITE,
            font=ctk.CTkFont(size=11, weight="bold"), corner_radius=8,
        )
        btn_them.pack(side="left", padx=10)

        ctk.CTkFrame(dialog, fg_color=BORDER, height=1, corner_radius=0).pack(fill="x", padx=16)

        # Vùng danh sách
        vung = ctk.CTkScrollableFrame(dialog, fg_color=BG, corner_radius=0,
                                      scrollbar_button_color=BORDER)
        vung.pack(fill="both", expand=True, padx=16, pady=(8, 16))

        # Tải và hiển thị danh sách
        def _tai_va_hien():
            for c in vung.winfo_children():
                c.destroy()
            ctk.CTkLabel(vung, text="⏳  Đang tải...",
                         font=ctk.CTkFont(size=12), text_color=TEXT_MUTED).pack(pady=30)
            def _fetch():
                try:
                    pass
                    parts = _evs.lay_nguoi_tham_gia_su_kien(su_kien.id)
                except Exception as e:
                    print(f"[events_page] Lỗi tải người tham gia: {e}")
                    traceback.print_exc()
                    parts = []
                
                try:
                    dialog.after(0, lambda p=parts: _render(p))
                except Exception as e:
                    print(f"[events_page] Lỗi cập nhật UI sau khi tải: {e}")
            threading.Thread(target=_fetch, daemon=True).start()

        def _render(parts):
            try:
                if not dialog.winfo_exists():
                    return
            except Exception:
                return
            for c in vung.winfo_children():
                c.destroy()
            if not parts:
                ctk.CTkLabel(vung, text="Chưa có ai đăng ký sự kiện này.",
                             font=ctk.CTkFont(size=12), text_color=TEXT_MUTED).pack(pady=40)
                return
            _TT = {"PENDING": "Chờ duyệt", "APPROVED": "Đã duyệt", "REJECTED": "Từ chối"}
            for p in parts:
                rf = ctk.CTkFrame(vung, fg_color=WHITE, corner_radius=10,
                                  border_width=1, border_color=BORDER)
                rf.pack(fill="x", pady=3)
                rf.grid_columnconfigure(1, weight=1)
                ctk.CTkLabel(rf, text=f"👤  {p.ten_hoi_vien}",
                             font=ctk.CTkFont(size=12, weight="bold"),
                             text_color=TEXT_PRIMARY, anchor="w").grid(
                    row=0, column=0, padx=14, pady=10, sticky="w")
                ngay = p.ngay_dang_ky[:10] if p.ngay_dang_ky else ""
                ctk.CTkLabel(rf, text=f"📅 {ngay}",
                             font=ctk.CTkFont(size=10), text_color=TEXT_MUTED).grid(
                    row=0, column=1, padx=4, sticky="w")
                mau_tt = ORANGE if p.trang_thai == "PENDING" else (
                    EMERALD if p.trang_thai == "APPROVED" else RED)
                ctk.CTkLabel(rf, text=_TT.get(p.trang_thai, p.trang_thai),
                             font=ctk.CTkFont(size=10, weight="bold"),
                             text_color=mau_tt).grid(row=0, column=2, padx=8)
                bf = ctk.CTkFrame(rf, fg_color="transparent")
                bf.grid(row=0, column=3, padx=(0, 8))
                if p.trang_thai == "PENDING":
                    ctk.CTkButton(bf, text="Duyệt", width=64, height=28,
                                  fg_color="#d1fae5", text_color=EMERALD,
                                  hover_color=EMERALD, corner_radius=8,
                                  command=lambda pt=p: _cap_nhat_tt(pt, "APPROVED")).pack(side="left", padx=(0, 4))
                    ctk.CTkButton(bf, text="Từ chối", width=72, height=28,
                                  fg_color="#fee2e2", text_color=RED,
                                  hover_color=RED, corner_radius=8,
                                  command=lambda pt=p: _cap_nhat_tt(pt, "REJECTED")).pack(side="left", padx=(0, 4))
                ctk.CTkButton(bf, text="Xóa", width=56, height=28,
                              fg_color="#f1f5f9", text_color=TEXT_SECONDARY,
                              hover_color="#fee2e2", corner_radius=8,
                              command=lambda pt=p: _xoa(pt)).pack(side="left")

        # Thêm người
        def _them():
            chon = combo_hv.get().strip()
            if not chon or " - " not in chon or chon.startswith("--"):
                self.app.hien_thong_bao("Vui lòng chọn hội viên!", "error")
                return
            phan = chon.split(" - ", 1)
            id_hv = phan[0].strip()
            ten_hv = _map_hv.get(id_hv, phan[1].strip() if len(phan) > 1 else "")
            btn_them.configure(state="disabled", text="Đang thêm...")
            def _do():
                try:
                    pass
                    existing = _evs.lay_nguoi_tham_gia_su_kien(su_kien.id)
                    if any(p.id_hoi_vien == id_hv for p in existing):
                        def _warn():
                            btn_them.configure(state="normal", text="＋  Thêm")
                            self.app.hien_thong_bao("Hội viên này đã tham gia sự kiện!", "error")
                        dialog.after(0, _warn)
                        return
                    from models.models import NguoiThamGiaSuKien
                    pt = NguoiThamGiaSuKien(
                        id=str(int(time.time() * 1000)),
                        id_su_kien=su_kien.id,
                        id_hoi_vien=id_hv,
                        ten_hoi_vien=ten_hv,
                        ngay_dang_ky=time.strftime("%Y-%m-%d"),
                        trang_thai="APPROVED",
                    )
                    _evs.them_nguoi_tham_gia(pt)
                    def _ok():
                        btn_them.configure(state="normal", text="＋  Thêm")
                        self.app.hien_thong_bao(f"Đã thêm {ten_hv} vào sự kiện!", "success")
                        _tai_va_hien()
                    dialog.after(0, _ok)
                except Exception as err:
                    def _fail(e=err):
                        btn_them.configure(state="normal", text="＋  Thêm")
                        self.app.hien_thong_bao(f"Lỗi: {e}", "error")
                    dialog.after(0, _fail)
            threading.Thread(target=_do, daemon=True).start()

        btn_them.configure(command=_them)

        # Xóa
        def _xoa(pt):
            def _do():
                try:
                    pass
                    _evs.xoa_nguoi_tham_gia_su_kien(pt.id)
                    def _ok():
                        self.app.hien_thong_bao("Đã xóa thành viên!", "success")
                        _tai_va_hien()
                    dialog.after(0, _ok)
                except Exception as err:
                    dialog.after(0, lambda e=err: self.app.hien_thong_bao(f"Lỗi xóa: {e}", "error"))
            threading.Thread(target=_do, daemon=True).start()

        # Cập nhật trạng thái
        def _cap_nhat_tt(pt, status):
            def _do():
                try:
                    pass
                    _evs.cap_nhat_trang_thai_nguoi_tham_gia(pt.id, status)
                    nhan = {"APPROVED": "Đã duyệt", "REJECTED": "Từ chối"}.get(status, status)
                    def _ok():
                        self.app.hien_thong_bao(f"Cập nhật: {nhan}!", "success")
                        _tai_va_hien()
                    dialog.after(0, _ok)
                except Exception as err:
                    dialog.after(0, lambda e=err: self.app.hien_thong_bao(f"Lỗi: {e}", "error"))
            threading.Thread(target=_do, daemon=True).start()

        _tai_va_hien()

