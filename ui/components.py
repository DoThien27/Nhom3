import customtkinter as ctk
import math
from typing import Callable, Any

# Define basic colors to avoid circular imports from app.py
ORANGE = "#ea580c"
ORANGE_DARK = "#c2410c"
ORANGE_LIGHT = "#ffedd5"
BG = "#f1f5f9"
WHITE = "#ffffff"
TEXT_PRIMARY = "#0f172a"
TEXT_SECONDARY = "#475569"
TEXT_MUTED = "#94a3b8"
BORDER = "#e2e8f0"
EMERALD = "#059669"
RED = "#dc2626"
BLUE = "#2563eb"


def clear_frame(frame: Any) -> None:
    """Xóa toàn bộ widget con của một frame."""
    for widget in frame.winfo_children():
        widget.destroy()


def calculate_responsive_columns(window_width: int, max_cols: int = 3, min_width: int = 350) -> int:
    """
    Tính số cột phù hợp cho layout dạng lưới (grid) dựa trên chiều rộng hiện tại.
    """
    if window_width <= 0:
        return max_cols  # Mặc định lúc chưa hiển thị
        
    cols = window_width // min_width
    return max(1, min(cols, max_cols))


def create_page_header(parent: Any, title: str, 
                       primary_action_text: str = None, 
                       primary_action_cmd: Callable = None,
                       search_placeholder: str = "Tìm kiếm...",
                       search_cmd: Callable = None,
                       filter_options: list = None,
                       filter_cmd: Callable = None) -> tuple:
    """
    Tạo header chuẩn gồm 2 dòng:
    Dòng 1: Tiêu đề + Nút hành động chính
    Dòng 2: Thanh tìm kiếm + Dropdown lọc (tùy chọn)
    
    Trả về: (header_frame, search_entry, filter_combobox)
    """
    header_frame = ctk.CTkFrame(parent, fg_color=WHITE, corner_radius=0)
    header_frame.pack(fill="x", padx=24, pady=(24, 16))

    # Dòng 1: Tiêu đề và nút hành động
    row1 = ctk.CTkFrame(header_frame, fg_color="transparent")
    row1.pack(fill="x", pady=(0, 16))
    
    ctk.CTkLabel(row1, text=title,
                 font=ctk.CTkFont(size=20, weight="bold"),
                 text_color=TEXT_PRIMARY).pack(side="left")

    if primary_action_text and primary_action_cmd:
        ctk.CTkButton(row1, text=primary_action_text,
                      fg_color=ORANGE, hover_color=ORANGE_DARK,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      height=36, corner_radius=8,
                      command=primary_action_cmd).pack(side="right")

    # Dòng 2: Tìm kiếm và bộ lọc
    row2 = ctk.CTkFrame(header_frame, fg_color="transparent")
    row2.pack(fill="x")
    
    search_entry = None
    if search_cmd:
        search_entry = ctk.CTkEntry(row2, placeholder_text=search_placeholder,
                                    width=250, height=36, corner_radius=8,
                                    border_color=BORDER)
        search_entry.pack(side="left")
        search_entry.bind("<KeyRelease>", search_cmd)

    filter_combo = None
    if filter_options and filter_cmd:
        filter_combo = ctk.CTkComboBox(row2, values=filter_options,
                                       width=150, height=36, corner_radius=8,
                                       border_color=BORDER, button_color=ORANGE,
                                       command=filter_cmd)
        filter_combo.set(filter_options[0])
        filter_combo.pack(side="left", padx=12)

    return header_frame, search_entry, filter_combo


def create_pagination(parent: Any, current_page: int, total_items: int, 
                      page_size: int, on_page_change: Callable) -> ctk.CTkFrame:
    """
    Tạo thanh điều hướng phân trang.
    """
    total_pages = max(1, math.ceil(total_items / page_size))
    
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    
    # Label thông tin
    start_idx = (current_page - 1) * page_size + 1 if total_items > 0 else 0
    end_idx = min(current_page * page_size, total_items)
    
    info_text = f"Hiển thị {start_idx}-{end_idx} trên {total_items}"
    ctk.CTkLabel(frame, text=info_text,
                 font=ctk.CTkFont(size=12), text_color=TEXT_MUTED).pack(side="left", padx=16)

    # Các nút điều hướng
    controls = ctk.CTkFrame(frame, fg_color="transparent")
    controls.pack(side="right", padx=16)

    def _go_prev():
        if current_page > 1:
            on_page_change(current_page - 1)

    def _go_next():
        if current_page < total_pages:
            on_page_change(current_page + 1)

    btn_prev = ctk.CTkButton(controls, text="◀ Trước", width=70, height=30,
                             fg_color=WHITE, text_color=TEXT_PRIMARY,
                             border_width=1, border_color=BORDER,
                             hover_color=BG, command=_go_prev,
                             state="normal" if current_page > 1 else "disabled")
    btn_prev.pack(side="left", padx=4)

    ctk.CTkLabel(controls, text=f"Trang {current_page} / {total_pages}",
                 font=ctk.CTkFont(size=12, weight="bold"),
                 text_color=TEXT_PRIMARY).pack(side="left", padx=12)

    btn_next = ctk.CTkButton(controls, text="Sau ▶", width=70, height=30,
                             fg_color=WHITE, text_color=TEXT_PRIMARY,
                             border_width=1, border_color=BORDER,
                             hover_color=BG, command=_go_next,
                             state="normal" if current_page < total_pages else "disabled")
    btn_next.pack(side="left", padx=4)

    return frame
