"""
app/services/event_service.py
─────────────────────────────
Quan ly su kien.
"""
from app.database import get_db_context
from app.models import SuKien


class EventService:
    @staticmethod
    def lay_tat_ca():
        with get_db_context() as (conn, cur):
            cur.execute("SELECT e.*, f.facility_name FROM Events e LEFT JOIN Facilities f ON e.facilityId=f.facility_id ORDER BY e.date DESC")
            return [SuKien(
                id=str(r.id), ten=r.name, mo_ta=r.description or '',
                ngay=str(r.date), gio=r.time or '', gio_ket_thuc='',
                dia_diem=r.location or '', suc_chua=r.capacity or 0,
                gia=float(r.price or 0), facility_id=r.facilityId,
                ten_san=r.facility_name, trang_thai=r.status or 'UPCOMING'
            ) for r in cur.fetchall()]
    
    @staticmethod
    def them(ev: SuKien):
        with get_db_context() as (conn, cur):
            cur.execute(
                "INSERT INTO Events (id, name, description, date, time, location, facilityId, capacity, price, status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (ev.id, ev.ten, ev.mo_ta, ev.ngay, ev.gio, ev.dia_diem, ev.facility_id, ev.suc_chua, ev.gia, ev.trang_thai)
            )
            conn.commit()
        return ev
    
    @staticmethod
    def sua(id, ten, mo_ta, ngay, gio, dia_diem, suc_chua, gia, facility_id, trang_thai):
        with get_db_context() as (conn, cur):
            cur.execute(
                "UPDATE Events SET name=%s, description=%s, date=%s, time=%s, location=%s, capacity=%s, price=%s, facilityId=%s, status=%s WHERE id=%s",
                (ten, mo_ta, ngay, gio, dia_diem, suc_chua, gia, facility_id, trang_thai, id)
            )
            conn.commit()
    
    @staticmethod
    def xoa(id):
        with get_db_context() as (conn, cur):
            cur.execute("DELETE FROM EventParticipants WHERE eventId=%s", (id,))
            cur.execute("DELETE FROM Events WHERE id=%s", (id,))
            conn.commit()
