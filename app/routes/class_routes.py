from flask import Blueprint, request, jsonify
from app.utils import safe_dict, roles_required, handle_db_error
from app.services import ClassService
from app.models import BuoiHoc
from app.database import get_db_context
import uuid
from datetime import datetime

class_bp = Blueprint('class_bp', __name__)

@class_bp.route('/api/classes', methods=['GET'])
@roles_required('ADMIN', 'PT')
def get_classes():
    try:
        data = ClassService.lay_tat_ca()
        return jsonify({'success': True, 'data': [safe_dict(c) for c in data]})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 500

@class_bp.route('/api/classes/<class_id>/enroll', methods=['POST'])
@roles_required('ADMIN', 'PT')
def enroll_member(class_id):
    try:
        member_id = request.json.get('memberId')
        with get_db_context() as (conn, cur):
            # 1. Check Capacity
            cur.execute("SELECT capacity, price, name FROM Classes WHERE id=%s", (class_id,))
            cls = cur.fetchone()
            cur.execute("SELECT COUNT(*) as c FROM ClassEnrollments WHERE classId=%s", (class_id,))
            if cur.fetchone()['c'] >= cls['capacity']: 
                return jsonify({'success': False, 'error': 'Lớp đã đầy'}), 400
            
            # 2. Check Member Card Status
            cur.execute("SELECT status, expiryDate FROM MemberCards WHERE memberId=%s AND status='ACTIVE' ORDER BY expiryDate DESC LIMIT 1", (member_id,))
            card = cur.fetchone()
            if not card:
                return jsonify({'success': False, 'error': 'Hội viên không có thẻ ACTIVE'}), 400
            if datetime.strptime(str(card['expiryDate']), '%Y-%m-%d') < datetime.now():
                return jsonify({'success': False, 'error': 'Thẻ hội viên đã hết hạn'}), 400
            
            # 3. Check for duplicates
            cur.execute("SELECT * FROM ClassEnrollments WHERE classId=%s AND memberId=%s", (class_id, member_id))
            if cur.fetchone():
                return jsonify({'success': False, 'error': 'Hội viên đã đăng ký lớp này'}), 400

            # 4. Create Enrollment
            cur.execute("INSERT INTO ClassEnrollments (classId, memberId) VALUES (%s,%s)", (class_id, member_id))

            # 5. Create Invoice if needed
            if float(cls['price'] or 0) > 0:
                inv_id = 'INV'+str(uuid.uuid4())[:8].upper()
                cur.execute("""INSERT INTO Invoices 
                    (id, memberId, sourceType, sourceId, totalAmount, discountAmount, finalAmount, paidAmount, remainingAmount, date, paymentMethod, paymentStatus, note) 
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (inv_id, member_id, 'CLASS', class_id, cls['price'], 0, cls['price'], 0, cls['price'], datetime.now().strftime('%Y-%m-%d'), 'CASH', 'UNPAID', f"Đăng ký lớp: {cls['name']}"))
            
            conn.commit()
        return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 500

@class_bp.route('/api/classes/<class_id>/enroll/<member_id>', methods=['DELETE'])
@roles_required('ADMIN', 'PT')
def unenroll_member(class_id, member_id):
    try:
        with get_db_context() as (conn, cur):
            cur.execute("DELETE FROM ClassEnrollments WHERE classId=%s AND memberId=%s", (class_id, member_id))
            cur.execute("UPDATE Invoices SET paymentStatus='CANCELLED' WHERE memberId=%s AND sourceId=%s AND sourceType='CLASS' AND paymentStatus='UNPAID'", (member_id, class_id))
            conn.commit()
        return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 500

@class_bp.route('/api/classes', methods=['POST'])
@roles_required('ADMIN', 'PT')
def add_class():
    try:
        data = request.json
        c = BuoiHoc(
            id=str(uuid.uuid4())[:8],
            name=data.get('name'),
            trainerId=data.get('trainerId'),
            sportId=data.get('sportId'),
            facilityId=data.get('facilityId'),
            time=data.get('time'),
            dayOfWeek=data.get('dayOfWeek'),
            capacity=int(data.get('capacity', 20)),
            price=float(data.get('price', 0)),
            status=data.get('status', 'ACTIVE')
        )
        ClassService.them(c)
        return jsonify({'success': True, 'class': safe_dict(c)})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 400

@class_bp.route('/api/classes/<id>', methods=['PUT'])
@roles_required('ADMIN', 'PT')
def update_class(id):
    try:
        data = request.json
        ClassService.sua(
            id, data.get('name'), data.get('trainerId'), data.get('sportId'),
            data.get('facilityId'), data.get('time'), data.get('dayOfWeek'),
            int(data.get('capacity', 20)), float(data.get('price', 0)), data.get('status', 'ACTIVE')
        )
        return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 400

@class_bp.route('/api/classes/<id>', methods=['DELETE'])
@roles_required('ADMIN')
def delete_class(id):
    try:
        ClassService.xoa(id)
        return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 500
