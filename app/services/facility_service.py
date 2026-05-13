"""
app/services/facility_service.py
────────────────────────────────
Quan ly san bai, co so vat chat.
"""
import uuid
from app.database import get_db_context


class FacilityService:
    @staticmethod
    def lay_tat_ca():
        with get_db_context() as (conn, cur):
            cur.execute("SELECT * FROM Facilities")
            return cur.fetchall()
    
    @staticmethod
    def them(facility_name, location):
        with get_db_context() as (conn, cur):
            facility_id = str(uuid.uuid4())[:8]
            cur.execute("INSERT INTO Facilities (facility_id, facility_name, location) VALUES (%s,%s,%s)", (facility_id, facility_name, location))
            conn.commit()
            return facility_id
    
    @staticmethod
    def sua(facility_id, facility_name, location):
        with get_db_context() as (conn, cur):
            cur.execute("UPDATE Facilities SET facility_name=%s, location=%s WHERE facility_id=%s", (facility_name, location, facility_id))
            conn.commit()
    
    @staticmethod
    def xoa(facility_id):
        with get_db_context() as (conn, cur):
            cur.execute("DELETE FROM Facilities WHERE facility_id=%s", (facility_id,))
            conn.commit()
