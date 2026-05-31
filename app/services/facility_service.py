"""
app/services/facility_service.py
────────────────────────────────
Quan ly san bai, co so vat chat.
"""
import uuid
from app.database import get_db_context
from app.utils import generate_sequential_id



class FacilityService:
    @staticmethod
    def lay_tat_ca():
        with get_db_context() as (conn, cur):
            cur.execute("""
                SELECT f.*, s.sport_name 
                FROM Facilities f 
                LEFT JOIN Sports s ON f.sport_id = s.sport_id
            """)
            return cur.fetchall()
    
    @staticmethod
    def them(facility_name, location, sport_id=None):
        with get_db_context() as (conn, cur):
            facility_id = generate_sequential_id('Facilities', 'FAC', 'facility_id')
            cur.execute("INSERT INTO Facilities (facility_id, facility_name, location, sport_id) VALUES (%s,%s,%s,%s)", (facility_id, facility_name, location, sport_id))
            conn.commit()
            return facility_id
    
    @staticmethod
    def sua(facility_id, facility_name, location, sport_id=None):
        with get_db_context() as (conn, cur):
            cur.execute("UPDATE Facilities SET facility_name=%s, location=%s, sport_id=%s WHERE facility_id=%s", (facility_name, location, sport_id, facility_id))
            conn.commit()
    
    @staticmethod
    def xoa(facility_id):
        with get_db_context() as (conn, cur):
            cur.execute("DELETE FROM Facilities WHERE facility_id=%s", (facility_id,))
            conn.commit()
