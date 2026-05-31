from app.database import get_db_context
from app.services.member_service import MemberService

class DashboardService:
    @staticmethod
    def lay_thong_ke():
        MemberService.cap_nhat_the_het_han()
        with get_db_context() as (conn, cur):
            # 1. Basic Stats
            cur.execute("SELECT COUNT(*) as c FROM Members")
            totalMembers = cur.fetchone()["c"] or 0
            
            cur.execute("SELECT COUNT(*) as c FROM Members WHERE status='ACTIVE'")
            activeMembers = cur.fetchone()["c"] or 0
            
            cur.execute("SELECT COUNT(*) as c FROM Invoices WHERE paymentStatus != 'PAID'")
            unpaidCount = cur.fetchone()["c"] or 0
            
            cur.execute("SELECT SUM(paidAmount) as s FROM Invoices")
            totalRevenue = cur.fetchone()["s"] or 0
            
            # 2. Classes Soon Full
            cur.execute("""
                SELECT c.name, c.capacity, 
                       (SELECT COUNT(*) FROM ClassEnrollments WHERE classId = c.id) as enrolled
                FROM Classes c
                HAVING enrolled >= capacity - 5 AND enrolled > 0
                LIMIT 10
            """)
            classesSoonFull = cur.fetchall()
            
            return {
                "totalMembers": totalMembers,
                "activeMembers": activeMembers,
                "unpaidCount": unpaidCount,
                "totalRevenue": float(totalRevenue or 0),
                "classesSoonFull": classesSoonFull
            }
