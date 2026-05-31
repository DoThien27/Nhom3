from app.database import get_db_context
from app.models import HoaDon

class InvoiceService:
    @staticmethod
    def lay_tat_ca(month=None):
        with get_db_context() as (conn, cur):
            sql = """SELECT i.*, m.fullName as memberName 
                     FROM Invoices i 
                     LEFT JOIN Members m ON i.memberId = m.id"""
            params = []
            if month:
                y, m = month.split('-')
                sql += " WHERE MONTH(i.date) = %s AND YEAR(i.date) = %s"
                params.extend([int(m), int(y)])
                
            sql += " ORDER BY CAST(SUBSTRING(i.id, 4) AS UNSIGNED) DESC"
            cur.execute(sql, tuple(params))
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
        from datetime import datetime, timedelta
        with get_db_context() as (conn, cur):
            cur.execute("SELECT * FROM Invoices WHERE id = %s", (id,))
            inv = cur.fetchone()
            if not inv: raise ValueError("Không tìm thấy hóa đơn")
            
            if amount <= 0:
                raise ValueError("Số tiền thanh toán phải lớn hơn 0")
            
            remaining = float(inv['remainingAmount'] or 0)
            if amount > remaining:
                raise ValueError("Số tiền thanh toán không được lớn hơn số tiền còn lại.")
            
            new_paid = float(inv['paidAmount'] or 0) + amount
            new_remaining = remaining - amount
            # Tránh số dư âm do sai số float
            if new_remaining < 0: new_remaining = 0
            new_status = 'PAID' if new_remaining == 0 else 'PARTIAL'
            
            sql = """UPDATE Invoices SET paidAmount=%s, remainingAmount=%s, paymentStatus=%s, paymentMethod=%s, note=%s WHERE id=%s"""
            cur.execute(sql, (new_paid, new_remaining, new_status, method, note or inv['note'], id))
            
            # Kích hoạt dịch vụ tương ứng nếu thanh toán đủ
            if new_status == 'PAID':
                if inv['sourceType'] == 'PLAN':
                    card_id = inv.get('relatedCardId')
                    plan_id = inv['sourceId']
                    member_id = inv['memberId']
                    if card_id:
                        # Tính ngày bắt đầu và kết thúc
                        cur.execute("SELECT durationMonths FROM Plans WHERE id=%s", (plan_id,))
                        plan = cur.fetchone()
                        duration = plan['durationMonths'] if plan and plan['durationMonths'] else 1
                        
                        # Tìm thẻ đang hoạt động để nối tiếp ngày
                        cur.execute("SELECT expiryDate FROM MemberCards WHERE memberId=%s AND status='ACTIVE' ORDER BY expiryDate DESC LIMIT 1", (member_id,))
                        active_card = cur.fetchone()
                        
                        today = datetime.now()
                        if active_card and active_card['expiryDate'] and active_card['expiryDate'] >= today.date():
                            # Nối tiếp ngày
                            start_date = active_card['expiryDate'] + timedelta(days=1)
                        else:
                            start_date = today.date()
                            
                        expiry_date = start_date + timedelta(days=30 * duration)
                        
                        cur.execute("UPDATE MemberCards SET status='ACTIVE', issueDate=%s, expiryDate=%s WHERE id=%s", 
                                    (start_date.strftime('%Y-%m-%d'), expiry_date.strftime('%Y-%m-%d'), card_id))
                    
                    cur.execute("UPDATE Members SET status='ACTIVE' WHERE id=%s", (inv['memberId'],))
                
                elif inv['sourceType'] == 'CLASS':
                    cur.execute("UPDATE ClassEnrollments SET status='ACTIVE' WHERE classId=%s AND memberId=%s", (inv['sourceId'], inv['memberId']))
                    if cur.rowcount == 0:
                        cur.execute("INSERT IGNORE INTO ClassEnrollments (classId, memberId, status) VALUES (%s, %s, 'ACTIVE')", (inv['sourceId'], inv['memberId']))
                    
                elif inv['sourceType'] == 'EVENT':
                    cur.execute("UPDATE EventParticipants SET status='CONFIRMED' WHERE eventId=%s AND memberId=%s", (inv['sourceId'], inv['memberId']))
                    if cur.rowcount == 0:
                        cur.execute("INSERT IGNORE INTO EventParticipants (eventId, memberId, status) VALUES (%s, %s, 'CONFIRMED')", (inv['sourceId'], inv['memberId']))
                
            conn.commit()
