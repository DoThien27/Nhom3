"""
app/services/sport_service.py
─────────────────────────────
Quan ly mon the thao.
"""
import uuid
from app.database import get_db_context
from app.utils import generate_sequential_id

class SportService:
    @staticmethod
    def lay_tat_ca():
        with get_db_context() as (conn, cur):
            sql = """
                SELECT 
                    s.*,
                    (SELECT COUNT(*) FROM Facilities WHERE sport_id = s.sport_id) as facilityCount,
                    (SELECT COUNT(*) FROM Classes WHERE sportId = s.sport_id AND status != 'CANCELLED') as classCount
                FROM Sports s
            """
            cur.execute(sql)
            return cur.fetchall()
    
    @staticmethod
    def them(sport_name, description):
        with get_db_context() as (conn, cur):
            sport_id = generate_sequential_id('Sports', 'SP', 'sport_id')
            cur.execute("INSERT INTO Sports (sport_id, sport_name, description) VALUES (%s,%s,%s)", (sport_id, sport_name, description))
            conn.commit()
            return sport_id
    
    @staticmethod
    def sua(sport_id, sport_name, description):
        with get_db_context() as (conn, cur):
            cur.execute("UPDATE Sports SET sport_name=%s, description=%s WHERE sport_id=%s", (sport_name, description, sport_id))
            conn.commit()
    
    @staticmethod
    def xoa(sport_id):
        with get_db_context() as (conn, cur):
            cur.execute("DELETE FROM Sports WHERE sport_id=%s", (sport_id,))
            conn.commit()
