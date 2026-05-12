from app.database import get_db_context
from datetime import datetime

class ReportService:
    @staticmethod
    def get_full_report():
        with get_db_context() as (conn, cur):
            # 1. Monthly Revenue
            cur.execute("SELECT SUM(paidAmount) as s FROM Invoices WHERE paymentStatus != 'CANCELLED' AND MONTH(date) = MONTH(CURRENT_DATE()) AND YEAR(date) = YEAR(CURRENT_DATE())")
            rev_month = cur.fetchone()["s"] or 0
            
            # 2. Total Revenue
            cur.execute("SELECT SUM(paidAmount) as s FROM Invoices WHERE paymentStatus != 'CANCELLED'")
            rev_total = cur.fetchone()["s"] or 0
            
            # 3. New Members this month
            cur.execute("SELECT COUNT(*) as c FROM Members WHERE MONTH(joinDate) = MONTH(CURRENT_DATE()) AND YEAR(joinDate) = YEAR(CURRENT_DATE())")
            new_members = cur.fetchone()["c"] or 0
            
            # 4. Active Classes
            cur.execute("SELECT COUNT(*) as c FROM Classes")
            active_classes = cur.fetchone()["c"] or 0
            
            # 5. Revenue by month (Chart)
            cur.execute("""
                SELECT DATE_FORMAT(date, '%Y-%m') as m, SUM(paidAmount) as s 
                FROM Invoices 
                WHERE paymentStatus != 'CANCELLED' 
                GROUP BY m 
                ORDER BY m ASC 
                LIMIT 12
            """)
            chart_data = [[r["m"], float(r["s"])] for r in cur.fetchall()]
            
            # 6. Members by Plan (Doughnut)
            cur.execute("""
                SELECT p.name, COUNT(m.id) as total 
                FROM Plans p 
                LEFT JOIN Members m ON p.id = m.activePlanId 
                GROUP BY p.id
            """)
            plan_data = [dict(r) for r in cur.fetchall()]
            
            # 7. Invoices by Status
            cur.execute("""
                SELECT paymentStatus as status, COUNT(*) as count, SUM(finalAmount) as total 
                FROM Invoices 
                GROUP BY paymentStatus
            """)
            status_data = [dict(r) for r in cur.fetchall()]
            
            # 8. Top Members
            cur.execute("""
                SELECT m.fullName as name, SUM(i.paidAmount) as total 
                FROM Invoices i 
                JOIN Members m ON i.memberId = m.id 
                WHERE i.paymentStatus != 'CANCELLED'
                GROUP BY m.id 
                ORDER BY total DESC 
                LIMIT 5
            """)
            top_members = [dict(r) for r in cur.fetchall()]
            
            return {
                "doanh_thu_thang": float(rev_month),
                "tong_doanh_thu": float(rev_total),
                "hoi_vien_moi": new_members,
                "lop_hoat_dong": active_classes,
                "dt_theo_thang": chart_data,
                "hv_theo_goi": plan_data,
                "hd_theo_tt": status_data,
                "top_hv": top_members
            }
