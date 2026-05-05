from typing import Optional, List
from database.db_connection import get_db_context
from models.models import NguoiDung
import bcrypt
from utils.logger import logger

def _hash_password(password: str) -> str:
    if not password:
        return password
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def dang_nhap(ten_dang_nhap: str, mat_khau: str) -> Optional[NguoiDung]:
    try:
        with get_db_context() as (conn, cur):
            # Check Users table
            cur.execute(
                "SELECT id, username, password, fullName, role, specialty, activeStudents "
                "FROM Users WHERE username=%s",
                (ten_dang_nhap,)
            )
            row = cur.fetchone()
            if row:
                db_password = row['password']
                is_valid = False
                needs_migration = False
                
                if db_password == mat_khau:
                    is_valid = True
                    needs_migration = True
                else:
                    try:
                        if bcrypt.checkpw(mat_khau.encode('utf-8'), db_password.encode('utf-8')):
                            is_valid = True
                    except ValueError:
                        pass # Invalid hash format
                
                if is_valid:
                    if needs_migration:
                        hashed = _hash_password(mat_khau)
                        cur.execute("UPDATE Users SET password=%s WHERE id=%s", (hashed, row['id']))
                        conn.commit()
                    
                    return NguoiDung(
                        id=row['id'], ten_dang_nhap=row['username'], ho_ten=row['fullName'],
                        vai_tro=row['role'], chuyen_mon=row['specialty'],
                        hoc_vien_dang_theo=row['activeStudents'] or 0
                    )
            
            # Check Members table
            cur.execute(
                "SELECT id, username, password, fullName, status "
                "FROM Members WHERE username=%s",
                (ten_dang_nhap,)
            )
            row = cur.fetchone()
            if row:
                db_password = row['password']
                is_valid = False
                needs_migration = False
                
                if db_password == mat_khau:
                    is_valid = True
                    needs_migration = True
                else:
                    try:
                        if bcrypt.checkpw(mat_khau.encode('utf-8'), db_password.encode('utf-8')):
                            is_valid = True
                    except ValueError:
                        pass
                
                if is_valid:
                    if needs_migration:
                        hashed = _hash_password(mat_khau)
                        cur.execute("UPDATE Members SET password=%s WHERE id=%s", (hashed, row['id']))
                        conn.commit()
                        
                    return NguoiDung(
                        id=row['id'], ten_dang_nhap=row['username'],
                        ho_ten=row['fullName'], vai_tro="MEMBER"
                    )
                    
            return None
    except Exception as e:
        logger.error(f"Database error in dang_nhap: {e}")
        raise

def lay_tat_ca() -> List[NguoiDung]:
    try:
        with get_db_context() as (conn, cur):
            cur.execute(
                "SELECT id, username, fullName, role, specialty, activeStudents FROM Users"
            )
            users = []
            for row in cur.fetchall():
                users.append(NguoiDung(
                    id=row['id'], ten_dang_nhap=row['username'], ho_ten=row['fullName'],
                    vai_tro=row['role'], chuyen_mon=row['specialty'],
                    hoc_vien_dang_theo=row['activeStudents'] or 0
                ))
            return users
    except Exception as e:
        logger.error(f"Database error in lay_tat_ca: {e}")
        raise

def them(nguoi_dung: NguoiDung) -> NguoiDung:
    try:
        with get_db_context() as (conn, cur):
            hashed_pwd = _hash_password(nguoi_dung.mat_khau) if nguoi_dung.mat_khau else None
            cur.execute(
                "INSERT INTO Users (id, username, password, fullName, role, specialty, activeStudents) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (nguoi_dung.id, nguoi_dung.ten_dang_nhap, hashed_pwd, nguoi_dung.ho_ten,
                nguoi_dung.vai_tro, nguoi_dung.chuyen_mon, nguoi_dung.hoc_vien_dang_theo or 0)
            )
            conn.commit()
        return nguoi_dung
    except Exception as e:
        logger.error(f"Database error in them (user): {e}")
        raise

def cap_nhat(nguoi_dung: NguoiDung) -> NguoiDung:
    try:
        with get_db_context() as (conn, cur):
            cur.execute(
                "UPDATE Users SET username=%s, fullName=%s, role=%s, specialty=%s, activeStudents=%s "
                "WHERE id=%s",
                (nguoi_dung.ten_dang_nhap, nguoi_dung.ho_ten, nguoi_dung.vai_tro, nguoi_dung.chuyen_mon,
                nguoi_dung.hoc_vien_dang_theo or 0, nguoi_dung.id)
            )
            if nguoi_dung.mat_khau:
                hashed_pwd = _hash_password(nguoi_dung.mat_khau)
                cur.execute("UPDATE Users SET password=%s WHERE id=%s", (hashed_pwd, nguoi_dung.id))
            conn.commit()
        return nguoi_dung
    except Exception as e:
        logger.error(f"Database error in cap_nhat (user): {e}")
        raise

def xoa(id_nguoi_dung: str) -> None:
    try:
        with get_db_context() as (conn, cur):
            cur.execute("DELETE FROM Users WHERE id=%s", (id_nguoi_dung,))
            conn.commit()
    except Exception as e:
        logger.error(f"Database error in xoa (user): {e}")
        raise
