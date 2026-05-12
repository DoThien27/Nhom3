import uuid
from datetime import datetime, timedelta
from app.database import get_db_context
from app.models import HoiVien, HoaDon
from .validators import Validators
from .user_service import UserService

class MemberService:
    @staticmethod
    def lay_tat_ca():
        with get_db_context() as (conn, cur):
            sql = """SELECT m.*, u.fullName as ptName, p.name as planName, p.price as planPrice
                     FROM Members m 
                     LEFT JOIN Users u ON m.assignedPTId=u.id 
                     LEFT JOIN Plans p ON m.activePlanId=p.id"""
            cur.execute(sql)
            return cur.fetchall()

    @staticmethod
    def them(hv: HoiVien):
        # Validation
        err = Validators.la_so_dien_thoai(hv.phone)
        if err: raise ValueError(err)
        if hv.email:
            err = Validators.la_email(hv.email)
            if err: raise ValueError(err)
        
        if hv.username and UserService.kiem_tra_trung_ten_dang_nhap(hv.username, hv.id): 
            raise ValueError("Tên đăng nhập đã tồn tại")
        
        if hv.password and not hv.password.startswith('$2b$'): 
            hv.password = Validators.bam_mat_khau(hv.password)
            
        with get_db_context() as (conn, cur):
            # Check if updating or creating
            cur.execute("SELECT activePlanId FROM Members WHERE id = %s", (hv.id,))
            old_data = cur.fetchone()
            old_plan_id = old_data['activePlanId'] if old_data else None

            # 1. Save Member
            sql = """REPLACE INTO Members (id, fullName, phone, email, joinDate, weight, username, password, homeTown, birthDate, gender, assignedPTId, activePlanId, status) 
                     VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            cur.execute(sql, (hv.id, hv.fullName, hv.phone, hv.email or '', 
                              hv.joinDate or datetime.now().strftime('%Y-%m-%d'), 
                              hv.weight, hv.username or None, hv.password or None, 
                              hv.homeTown, hv.birthDate or None, hv.gender, 
                              hv.assignedPTId or None, hv.activePlanId or None, 
                              hv.status))

            # 2. If plan assigned/changed, handle Card and Invoice
            if hv.activePlanId and hv.activePlanId != old_plan_id:
                cur.execute("SELECT * FROM Plans WHERE id = %s", (hv.activePlanId,))
                plan = cur.fetchone()
                if plan:
                    # Create/Update Card
                    card_id = str(uuid.uuid4())[:8].upper()
                    expiry = (datetime.now() + timedelta(days=30 * (plan['durationMonths'] or 1))).strftime('%Y-%m-%d')
                    
                    cur.execute("DELETE FROM MemberCards WHERE memberId = %s", (hv.id,))
                    cur.execute("INSERT INTO MemberCards (id, memberId, planId, issueDate, expiryDate, status, cardNumber) VALUES (%s, %s, %s, %s, %s, 'INACTIVE', %s)",
                                (card_id, hv.id, hv.activePlanId, datetime.now().strftime('%Y-%m-%d'), expiry, 'CARD'+card_id))
                    
                    # Create Invoice
                    inv_id = 'INV'+str(uuid.uuid4())[:8].upper()
                    
                    sql_inv = """INSERT INTO Invoices (id, memberId, sourceType, sourceId, totalAmount, discountAmount, finalAmount, paidAmount, remainingAmount, date, paymentMethod, paymentStatus, note) 
                                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                    cur.execute(sql_inv, (inv_id, hv.id, 'PLAN', hv.activePlanId, float(plan['price']), 0, float(plan['price']), 0, float(plan['price']), datetime.now().strftime('%Y-%m-%d'), 'CASH', 'UNPAID', f"Gói tập: {plan['name']}"))

                    # Set member to PENDING until paid
                    cur.execute("UPDATE Members SET status='PENDING' WHERE id=%s", (hv.id,))

            conn.commit()
        return hv

    @staticmethod
    def xoa(id):
        with get_db_context() as (conn, cur):
            cur.execute("SELECT COUNT(*) as c FROM Invoices WHERE memberId=%s AND paymentStatus != 'PAID' AND sourceType='PLAN'", (id,))
            if cur.fetchone()['c'] > 0:
                raise ValueError("Không thể xóa hội viên còn hóa đơn gói tập chưa thanh toán")
            
            cur.execute("DELETE FROM MemberCards WHERE memberId=%s", (id,))
            cur.execute("DELETE FROM Members WHERE id=%s", (id,))
            conn.commit()
