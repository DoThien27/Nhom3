from flask import Blueprint, request, jsonify
from app.utils import safe_dict, roles_required, handle_db_error
from app.services import ClassService
from app.models import BuoiHoc
from app.database import get_db_context
from app.utils import generate_sequential_id
from datetime import datetime

class_bp = Blueprint('class_bp', __name__)

def check_class_overlap(trainerId, facilityId, start_date_str, end_date_str, time_str, dayOfWeek_str, exclude_class_id=None):
    if not (start_date_str and end_date_str and time_str and dayOfWeek_str):
        return None

    try:
        new_start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        new_end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except Exception:
        return None

    try:
        t_parts = [t.strip() for t in time_str.split('-')]
        if len(t_parts) != 2: return None
        new_start_mins = int(t_parts[0].split(':')[0])*60 + int(t_parts[0].split(':')[1])
        new_end_mins = int(t_parts[1].split(':')[0])*60 + int(t_parts[1].split(':')[1])
    except Exception:
        return None

    new_days = set([d.strip() for d in dayOfWeek_str.split(',')])

    with get_db_context() as (conn, cur):
        sql = "SELECT * FROM Classes WHERE (trainerId=%s OR facilityId=%s) AND status='ACTIVE'"
        params = [trainerId, facilityId]
        if exclude_class_id:
            sql += " AND id != %s"
            params.append(exclude_class_id)
        cur.execute(sql, tuple(params))
        classes = cur.fetchall()

    for c in classes:
        if not c['startDate'] or not c['endDate']: continue
        if c['endDate'] < new_start_date or c['startDate'] > new_end_date: continue

        if not c['dayOfWeek']: continue
        c_days = set([d.strip() for d in c['dayOfWeek'].split(',')])
        if not new_days.intersection(c_days): continue

        if not c['time']: continue
        try:
            t_parts = [t.strip() for t in c['time'].split('-')]
            if len(t_parts) != 2: continue
            c_start_mins = int(t_parts[0].split(':')[0])*60 + int(t_parts[0].split(':')[1])
            c_end_mins = int(t_parts[1].split(':')[0])*60 + int(t_parts[1].split(':')[1])
        except Exception:
            continue

        if c_end_mins <= new_start_mins or c_start_mins >= new_end_mins: continue
            
        reason = "Huấn luyện viên" if c['trainerId'] == trainerId else "Sân bãi"
        return f"Lớp học bị trùng lịch (trùng {reason}) với lớp: {c['name']} ({c['time']} {c['dayOfWeek']})"

    return None


@class_bp.route('/api/classes', methods=['GET'])
@roles_required('ADMIN')
def get_classes():
    try:
        data = ClassService.lay_tat_ca()
        return jsonify({'success': True, 'data': [safe_dict(c) for c in data]})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 500

@class_bp.route('/api/classes/<class_id>/enroll', methods=['POST'])
@roles_required('ADMIN')
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
            status = 'ACTIVE' if float(cls['price'] or 0) == 0 else 'PENDING'
            cur.execute("INSERT INTO ClassEnrollments (classId, memberId, status) VALUES (%s,%s,%s)", (class_id, member_id, status))

            # 5. Create Invoice if needed
            if float(cls['price'] or 0) > 0:
                inv_id = generate_sequential_id('Invoices', 'INV')
                cur.execute("""INSERT INTO Invoices 
                    (id, memberId, sourceType, sourceId, totalAmount, discountAmount, finalAmount, paidAmount, remainingAmount, date, paymentMethod, paymentStatus, note) 
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (inv_id, member_id, 'CLASS', class_id, cls['price'], 0, cls['price'], 0, cls['price'], datetime.now().strftime('%Y-%m-%d'), 'CASH', 'UNPAID', f"Đăng ký lớp: {cls['name']}"))
            
            conn.commit()
        return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 500

@class_bp.route('/api/classes/<class_id>/enroll/<member_id>', methods=['DELETE'])
@roles_required('ADMIN')
def unenroll_member(class_id, member_id):
    try:
        with get_db_context() as (conn, cur):
            cur.execute("DELETE FROM ClassEnrollments WHERE classId=%s AND memberId=%s", (class_id, member_id))
            cur.execute("UPDATE Invoices SET paymentStatus='CANCELLED' WHERE memberId=%s AND sourceId=%s AND sourceType='CLASS' AND paymentStatus='UNPAID'", (member_id, class_id))
            conn.commit()
        return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 500

@class_bp.route('/api/classes', methods=['POST'])
@roles_required('ADMIN')
def add_class():
    try:
        data = request.json
        overlap_err = check_class_overlap(data.get('trainerId'), data.get('facilityId'), data.get('startDate'), data.get('endDate'), data.get('time'), data.get('dayOfWeek'))
        if overlap_err:
            return jsonify({'success': False, 'error': overlap_err}), 400

        c = BuoiHoc(
            id=generate_sequential_id('Classes', 'CLS'),
            name=data.get('name'),
            trainerId=data.get('trainerId'),
            sportId=data.get('sportId'),
            facilityId=data.get('facilityId'),
            time=data.get('time'),
            dayOfWeek=data.get('dayOfWeek'),
            capacity=int(data.get('capacity', 20)),
            price=float(data.get('price', 0)),
            status=data.get('status', 'ACTIVE'),
            startDate=data.get('startDate'),
            endDate=data.get('endDate')
        )
        ClassService.them(c)
        return jsonify({'success': True, 'class': safe_dict(c)})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 400

@class_bp.route('/api/classes/<id>', methods=['PUT'])
@roles_required('ADMIN')
def update_class(id):
    try:
        data = request.json
        overlap_err = check_class_overlap(data.get('trainerId'), data.get('facilityId'), data.get('startDate'), data.get('endDate'), data.get('time'), data.get('dayOfWeek'), id)
        if overlap_err:
            return jsonify({'success': False, 'error': overlap_err}), 400

        ClassService.sua(
            id, data.get('name'), data.get('trainerId'), data.get('sportId'),
            data.get('facilityId'), data.get('time'), data.get('dayOfWeek'),
            int(data.get('capacity', 20)), float(data.get('price', 0)), data.get('status', 'ACTIVE'),
            data.get('startDate'), data.get('endDate')
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
