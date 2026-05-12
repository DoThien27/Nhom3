from app.database import get_db_context
from app.models import HoaDon

class InvoiceService:
    @staticmethod
    def lay_tat_ca():
        with get_db_context() as (conn, cur):
            sql = """SELECT i.*, m.fullName as memberName 
                     FROM Invoices i 
                     LEFT JOIN Members m ON i.memberId = m.id
                     ORDER BY i.date DESC"""
            cur.execute(sql)
            return cur.fetchall()

    @staticmethod
    def them(inv: HoaDon):
        with get_db_context() as (conn, cur):
            sql = """INSERT INTO Invoices (id, memberId, sourceType, sourceId, totalAmount, discountAmount, finalAmount, paidAmount, remainingAmount, date, paymentMethod, paymentStatus, note) 
                     VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            cur.execute(sql, (inv.id, inv.memberId, inv.sourceType, inv.sourceId, inv.totalAmount, inv.discountAmount, inv.finalAmount, inv.paidAmount, inv.remainingAmount, inv.date, inv.paymentMethod, inv.paymentStatus, inv.note))
            conn.commit()
        return inv

    @staticmethod
    def thanh_toan(id, amount, method, note):
        with get_db_context() as (conn, cur):
            cur.execute("SELECT * FROM Invoices WHERE id = %s", (id,))
            inv = cur.fetchone()
            if not inv: raise ValueError("Không tìm thấy hóa đơn")
            
            new_paid = float(inv['paidAmount'] or 0) + amount
            new_remaining = float(inv['finalAmount'] or 0) - new_paid
            new_status = 'PAID' if new_remaining <= 0 else 'PARTIAL'
            
            sql = """UPDATE Invoices SET paidAmount=%s, remainingAmount=%s, paymentStatus=%s, paymentMethod=%s, note=%s WHERE id=%s"""
            cur.execute(sql, (new_paid, new_remaining, new_status, method, note or inv['note'], id))
            
            # If paid for a PLAN, activate member and card
            if new_status == 'PAID' and inv['sourceType'] == 'PLAN':
                cur.execute("UPDATE Members SET status='ACTIVE' WHERE id=%s", (inv['memberId'],))
                cur.execute("UPDATE MemberCards SET status='ACTIVE' WHERE memberId=%s AND planId=%s", (inv['memberId'], inv['sourceId']))
                
            conn.commit()
