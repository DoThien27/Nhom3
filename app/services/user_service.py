"""
app/services/user_service.py
────────────────────────────
Quan ly Users (ADMIN, PT) va xac thuc dang nhap.
"""
import uuid
from app.database import get_db_context
from app.models import NguoiDung
from .validators import Validators


class UserService:
    @staticmethod
    def kiem_tra_trung_ten_dang_nhap(username: str, current_id=None) -> bool:
        with get_db_context() as (conn, cur):
            cur.execute("SELECT id FROM Users WHERE username=%s", (username,))
            r = cur.fetchone()
            if r and (not current_id or str(r["id"]) != str(current_id)):
                return True
            cur.execute("SELECT id FROM Members WHERE username=%s", (username,))
            r = cur.fetchone()
            if r and (not current_id or str(r["id"]) != str(current_id)):
                return True
        return False

    @staticmethod
    def dang_nhap(username: str, password: str):
        if not username or not password:
            return None
        username = username.strip()
        try:
            with get_db_context() as (conn, cur):
                # Tim trong bang Users (ADMIN / PT)
                cur.execute("SELECT * FROM Users WHERE username=%s", (username,))
                row = cur.fetchone()
                if row and Validators.kiem_tra_mat_khau(password, row["password"]):
                    return NguoiDung(
                        id=row["id"], username=row["username"],
                        fullName=row["fullName"], role=row["role"],
                        specialty=row.get("specialty"),
                        activeStudents=row.get("activeStudents", 0),
                        phone=row.get("phone"), address=row.get("address"),
                    )
                # Tim trong bang Members
                cur.execute("SELECT * FROM Members WHERE username=%s", (username,))
                row = cur.fetchone()
                if row and Validators.kiem_tra_mat_khau(password, row["password"] or ""):
                    return NguoiDung(
                        id=row["id"], username=row["username"],
                        fullName=row["fullName"], role="MEMBER",
                    )
        except Exception as e:
            from app.database import logger
            logger.error(f"Login error: {e}")
        return None

    @staticmethod
    def lay_tat_ca():
        with get_db_context() as (conn, cur):
            cur.execute("SELECT id, username, fullName, role, specialty, phone, address, activeStudents FROM Users")
            return cur.fetchall()

    @staticmethod
    def them(data: dict):
        uid = str(uuid.uuid4())[:12]
        pw = Validators.bam_mat_khau(data.get("password", "123456"))
        with get_db_context() as (conn, cur):
            cur.execute(
                "INSERT INTO Users (id, username, password, fullName, role, specialty, phone, address) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (uid, data["username"], pw, data["fullName"], data.get("role", "PT"),
                 data.get("specialty"), data.get("phone"), data.get("address")),
            )
            conn.commit()
        return uid

    @staticmethod
    def sua(uid: str, data: dict):
        with get_db_context() as (conn, cur):
            cur.execute(
                "UPDATE Users SET fullName=%s, role=%s, specialty=%s, phone=%s, address=%s WHERE id=%s",
                (data["fullName"], data.get("role", "PT"),
                 data.get("specialty"), data.get("phone"), data.get("address"), uid),
            )
            if data.get("password"):
                pw = Validators.bam_mat_khau(data["password"])
                cur.execute("UPDATE Users SET password=%s WHERE id=%s", (pw, uid))
            conn.commit()

    @staticmethod
    def xoa(uid: str):
        with get_db_context() as (conn, cur):
            cur.execute("DELETE FROM Users WHERE id=%s", (uid,))
            conn.commit()
