from app.database import get_db_context
from app.models import GoiTap

class PlanService:
    @staticmethod
    def lay_tat_ca():
        with get_db_context() as (conn, cur):
            cur.execute("SELECT * FROM Plans")
            return cur.fetchall()

    @staticmethod
    def them(p: GoiTap):
        with get_db_context() as (conn, cur):
            sql = """INSERT INTO Plans (id, name, type, price, description, durationMonths) VALUES (%s,%s,%s,%s,%s,%s)"""
            cur.execute(sql, (p.id, p.name, p.type, p.price, p.description, p.durationMonths))
            conn.commit()
        return p

    @staticmethod
    def sua(id, name, type, price, durationMonths, description):
        with get_db_context() as (conn, cur):
            sql = """UPDATE Plans SET name=%s, type=%s, price=%s, durationMonths=%s, description=%s WHERE id=%s"""
            cur.execute(sql, (name, type, price, durationMonths, description, id))
            conn.commit()

    @staticmethod
    def xoa(id):
        with get_db_context() as (conn, cur):
            # Check for members using this plan
            cur.execute("SELECT COUNT(*) as c FROM Members WHERE activePlanId=%s", (id,))
            if cur.fetchone()['c'] > 0:
                raise ValueError("Không thể xóa gói tập đang có hội viên sử dụng")
            cur.execute("DELETE FROM Plans WHERE id=%s", (id,))
            conn.commit()
