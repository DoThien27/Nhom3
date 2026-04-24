"""
Sports Club Pro System — Entry Point
Chạy: python main.py
"""
import sys
import os

# Thêm thư mục gốc vào sys.path để import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from ui.app import SportsClubApp


if __name__ == "__main__":
    app = SportsClubApp()
    app.mainloop()
