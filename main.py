"""
Hệ Thống Quản Lý Câu Lạc Bộ Thể Thao — Entry Point
Chay: python main.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
import customtkinter as ctk
from ui.app import UngDungCauLacBo


def _kich_hoat_cuon_nhanh(root: tk.Misc, toc_do: int = 5) -> None:
    """
    Gắn một handler cuộn chuột toàn cục vào cửa sổ gốc.

    Cách hoạt động:
    - Với mỗi sự kiện <MouseWheel>, hàm đi ngược từ widget đang nhận event
      lên cây widget cho đến khi tìm được tk.Canvas đầu tiên.
    - Cuộn Canvas đó với tốc độ `toc_do` lần so với mặc định CTk (1 unit).
    - Dùng bind_all (không có add="+") để GHI ĐÈ hoàn toàn handler của
      CTkScrollableFrame — tránh xung đột và double-scroll.
    """

    def _tim_canvas(widget):
        """Đi ngược cây widget để tìm tk.Canvas đầu tiên."""
        while widget is not None:
            if isinstance(widget, tk.Canvas):
                return widget
            widget = getattr(widget, "master", None)
        return None

    def _cuon(event):
        canvas = _tim_canvas(event.widget)
        if canvas is None:
            return
        if sys.platform == "win32":
            # Windows: event.delta = ±120 mỗi notch
            canvas.yview_scroll(int(-1 * event.delta / 120 * toc_do), "units")
        elif sys.platform == "darwin":
            # macOS: event.delta nhỏ hơn
            canvas.yview_scroll(int(-1 * event.delta * toc_do), "units")

    def _cuon_linux_up(event):
        canvas = _tim_canvas(event.widget)
        if canvas:
            canvas.yview_scroll(-toc_do, "units")

    def _cuon_linux_down(event):
        canvas = _tim_canvas(event.widget)
        if canvas:
            canvas.yview_scroll(toc_do, "units")

    # Ghi đè bind_all — thay thế hoàn toàn handler của CTkScrollableFrame
    root.bind_all("<MouseWheel>",  _cuon)
    if sys.platform == "linux":
        root.bind_all("<Button-4>", _cuon_linux_up)
        root.bind_all("<Button-5>", _cuon_linux_down)


if __name__ == "__main__":
    app = UngDungCauLacBo()
    _kich_hoat_cuon_nhanh(app, toc_do=5)  # 5x nhanh hơn mặc định
    app.mainloop()
