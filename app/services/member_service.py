"""
app/services/member_service.py
──────────────────────────────
Quan ly hoi vien: INSERT rieng, UPDATE rieng, khong dung REPLACE INTO
de tranh mat du lieu FK (the, hoa don, lich su check-in).
"""
import uuid
from datetime import datetime, timedelta
from app.utils import generate_sequential_id

from app.database import get_db_context
from app.models import HoiVien, HoaDon
from .validators import Validators
from .user_service import UserService


class MemberService:
    @staticmethod
    def cap_nhat_the_het_han():
        with get_db_context() as (conn, cur):
            today = datetime.now().strftime('%Y-%m-%d')
            cur.execute("UPDATE MemberCards SET status='EXPIRED' WHERE status='ACTIVE' AND expiryDate < %s", (today,))
            cur.execute("""
                UPDATE Members 
                SET status='EXPIRED' 
                WHERE status='ACTIVE' AND EXISTS (
                    SELECT 1 FROM MemberCards mc WHERE mc.memberId = Members.id AND mc.status='EXPIRED'
                ) AND NOT EXISTS (
                    SELECT 1 FROM MemberCards mc WHERE mc.memberId = Members.id AND mc.status='ACTIVE'
                )
            """)
            conn.commit()

    @staticmethod
    def lay_tat_ca():
        MemberService.cap_nhat_the_het_han()
        with get_db_context() as (conn, cur):

            sql = """SELECT m.*, u.fullName as ptName, p.name as planName, p.price as planPrice
                     FROM Members m
                     LEFT JOIN Users u ON m.assignedPTId=u.id
                     LEFT JOIN Plans p ON m.activePlanId=p.id
                     ORDER BY m.createdAt DESC"""
            cur.execute(sql)
            return cur.fetchall()

    @staticmethod
    def them(hv: HoiVien):
        """
        Thêm mới hội viên (INSERT).
        Nếu có gói tập (activePlanId), tạo MemberCard INACTIVE và Invoice UNPAID.
        Hội viên chỉ ACTIVE khi thanh toán xong qua InvoiceService.thanh_toan().
        """
        # Validation
        err = Validators.la_so_dien_thoai(hv.phone)
        if err:
            raise ValueError(err)
        if hv.email:
            err = Validators.la_email(hv.email)
            if err:
                raise ValueError(err)

        if hv.username and UserService.kiem_tra_trung_ten_dang_nhap(hv.username, hv.id):
            raise ValueError("Tên đăng nhập đã tồn tại")

        if hv.password and not hv.password.startswith('$2b$'):
            hv.password = Validators.bam_mat_khau(hv.password)

        with get_db_context() as (conn, cur):
            # INSERT thành viên mới
            sql = """INSERT INTO Members
                     (id, fullName, phone, email, joinDate, weight, previousWeight, username, password,
                      homeTown, birthDate, gender, assignedPTId, activePlanId, status)
                     VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            cur.execute(sql, (
                hv.id, hv.fullName, hv.phone, hv.email or '',
                hv.joinDate or datetime.now().strftime('%Y-%m-%d'),
                hv.weight, hv.previousWeight, hv.username or None, hv.password or None,
                hv.homeTown, hv.birthDate or None, hv.gender,
                hv.assignedPTId or None, hv.activePlanId or None,
                hv.status
            ))

            # Nếu có gói tập → tạo thẻ INACTIVE + hóa đơn UNPAID
            if hv.activePlanId:
                MemberService._tao_the_va_hoa_don(cur, hv.id, hv.activePlanId)

            conn.commit()
        return hv

    @staticmethod
    def cap_nhat(id: str, data: dict):
        """
        Cập nhật thông tin hội viên (UPDATE, không đụng đến gói tập).
        """
        with get_db_context() as (conn, cur):
            # Cập nhật thông tin cơ bản
            sql = """UPDATE Members SET
                         fullName=%s, phone=%s, email=%s, birthDate=%s, gender=%s,
                         homeTown=%s, assignedPTId=%s, weight=%s, previousWeight=%s
                     WHERE id=%s"""
            cur.execute(sql, (
                data.get('fullName'), data.get('phone'), data.get('email') or '',
                data.get('birthDate') or None, data.get('gender', 'Nam'),
                data.get('homeTown'), data.get('assignedPTId') or None,
                float(data.get('weight', 0) or 0), float(data.get('previousWeight', 0) or 0),
                id
            ))
            conn.commit()

    @staticmethod
    def huy_goi_tap(id: str):
        with get_db_context() as (conn, cur):
            cur.execute("SELECT activePlanId FROM Members WHERE id = %s", (id,))
            existing = cur.fetchone()
            if existing and existing['activePlanId']:
                old_plan = existing['activePlanId']
                cur.execute("UPDATE MemberCards SET status='REVOKED' WHERE memberId=%s AND planId=%s AND status IN ('ACTIVE', 'INACTIVE', 'PENDING')", (id, old_plan))
                cur.execute("UPDATE Invoices SET paymentStatus='CANCELLED' WHERE memberId=%s AND sourceId=%s AND paymentStatus='UNPAID'", (id, old_plan))
                cur.execute("UPDATE Members SET activePlanId=NULL, status='INACTIVE' WHERE id=%s", (id,))
            conn.commit()

    @staticmethod
    def dang_ky_goi_tap(id: str, plan_id: str):
        with get_db_context() as (conn, cur):
            cur.execute("SELECT activePlanId FROM Members WHERE id = %s", (id,))
            existing = cur.fetchone()
            if existing and existing['activePlanId']:
                raise ValueError("Hội viên đang có gói tập. Vui lòng hủy gói cũ hoặc dùng chức năng đổi gói.")
            
            cur.execute("UPDATE Members SET activePlanId=%s, status='PENDING' WHERE id=%s", (plan_id, id))
            MemberService._tao_the_va_hoa_don(cur, id, plan_id)
            conn.commit()

    @staticmethod
    def doi_goi_tap(id: str, new_plan_id: str):
        with get_db_context() as (conn, cur):
            cur.execute("SELECT status FROM Members WHERE id = %s", (id,))
            m = cur.fetchone()
            if m and m['status'] == 'ACTIVE':
                raise ValueError("Gói tập hiện tại vẫn đang hoạt động. Vui lòng bấm 'Hủy gói' cũ trước khi muốn đổi sang gói mới.")
        MemberService.huy_goi_tap(id)
        MemberService.dang_ky_goi_tap(id, new_plan_id)

    @staticmethod
    def gia_han(id: str):
        """
        Gia hạn gói tập hiện tại của hội viên. Tạo thẻ mới và hóa đơn mới.
        """
        with get_db_context() as (conn, cur):
            cur.execute("SELECT activePlanId FROM Members WHERE id = %s", (id,))
            existing = cur.fetchone()
            if not existing or not existing['activePlanId']:
                raise ValueError("Hội viên chưa có gói tập nào để gia hạn")
            
            # Tạo thẻ và hóa đơn mới cho gói tập hiện tại
            MemberService._tao_the_va_hoa_don(cur, id, existing['activePlanId'])
            conn.commit()

    @staticmethod
    def _tao_the_va_hoa_don(cur, member_id: str, plan_id: str):
        """
        Tạo MemberCard (INACTIVE) và Invoice (UNPAID) cho gói tập mới.
        Thẻ chỉ ACTIVE khi hóa đơn được thanh toán đủ.
        Hàm này chạy trong transaction của caller (không commit ở đây).
        """
        cur.execute("SELECT * FROM Plans WHERE id = %s", (plan_id,))
        plan = cur.fetchone()
        if not plan:
            return

        # Tạo thẻ mới (INACTIVE, chờ thanh toán)
        card_id = generate_sequential_id('MemberCards', 'CRD')
        expiry = (datetime.now() + timedelta(days=30 * (plan['durationMonths'] or 1))).strftime('%Y-%m-%d')
        card_number = 'CARD' + card_id

        cur.execute(
            """INSERT INTO MemberCards (id, memberId, planId, issueDate, expiryDate, status, cardNumber)
               VALUES (%s, %s, %s, %s, %s, 'INACTIVE', %s)""",
            (card_id, member_id, plan_id, datetime.now().strftime('%Y-%m-%d'), expiry, card_number)
        )

        # Tạo hóa đơn UNPAID
        inv_id = generate_sequential_id('Invoices', 'INV')
        cur.execute(
            """INSERT INTO Invoices
               (id, memberId, sourceType, sourceId, relatedCardId, totalAmount, discountAmount, finalAmount,
                paidAmount, remainingAmount, date, paymentMethod, paymentStatus, note)
               VALUES (%s,%s,'PLAN',%s,%s,%s,0,%s,0,%s,%s,'CASH','UNPAID',%s)""",
            (inv_id, member_id, plan_id, card_id,
             float(plan['price']), float(plan['price']), float(plan['price']),
             datetime.now().strftime('%Y-%m-%d'),
             f"Gói tập: {plan['name']}")
        )

        # Đặt hội viên về PENDING (chờ thanh toán)
        cur.execute("UPDATE Members SET status='PENDING' WHERE id=%s", (member_id,))

    @staticmethod
    def xoa(id):
        with get_db_context() as (conn, cur):
            # Kiểm tra trạng thái hoạt động
            cur.execute("SELECT status FROM Members WHERE id=%s", (id,))
            m = cur.fetchone()
            if m and m['status'] == 'ACTIVE':
                raise ValueError("Không thể xóa hội viên đang ở trạng thái Hoạt động. Vui lòng hủy gói tập của hội viên này trước.")

            # Kiểm tra hóa đơn chưa thanh toán
            cur.execute(
                "SELECT COUNT(*) as c FROM Invoices WHERE memberId=%s AND paymentStatus NOT IN ('PAID','CANCELLED') AND sourceType='PLAN'",
                (id,)
            )
            if cur.fetchone()['c'] > 0:
                raise ValueError("Không thể xóa hội viên còn hóa đơn gói tập chưa thanh toán")

            # Xóa theo thứ tự FK
            cur.execute("DELETE FROM CheckIns WHERE memberId=%s", (id,))
            cur.execute("DELETE FROM ClassEnrollments WHERE memberId=%s", (id,))
            cur.execute("DELETE FROM EventParticipants WHERE memberId=%s", (id,))
            cur.execute("DELETE FROM MemberCards WHERE memberId=%s", (id,))
            cur.execute("DELETE FROM Invoices WHERE memberId=%s", (id,))
            cur.execute("DELETE FROM Members WHERE id=%s", (id,))
            conn.commit()
