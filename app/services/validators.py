"""
app/services/validators.py
──────────────────────────
Validation helpers & password hashing.
"""
import re
import bcrypt


class Validators:
    @staticmethod
    def bam_mat_khau(pw: str) -> str:
        return bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8") if pw else pw

    @staticmethod
    def kiem_tra_mat_khau(pw: str, hashed: str) -> bool:
        if pw == hashed:
            return True
        try:
            return bcrypt.checkpw(pw.encode("utf-8"), hashed.encode("utf-8"))
        except Exception:
            return False

    @staticmethod
    def la_so_dien_thoai(v: str):
        if not v:
            return "So dien thoai khong duoc de trong."
        if not re.fullmatch(r"0\d{9}", v.strip()):
            return "So dien thoai phai co 10 chu so va bat dau bang 0."
        return None

    @staticmethod
    def la_email(v: str):
        if not v or not v.strip():
            return None
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", v.strip()):
            return "Dia chi email khong hop le."
        return None
