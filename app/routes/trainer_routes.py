"""
app/routes/trainer_routes.py
─────────────────────────────
Quản lý huấn luyện viên (Users có role=PT):
- GET/POST/PUT/DELETE /api/trainers
- Chấm công: GET/POST/DELETE /api/trainer-attendance
- Lương: GET/POST(calculate)/PUT(pay) /api/trainer-salary
- Payroll tổng hợp: GET /api/trainer-payroll
"""
from flask import Blueprint, request, jsonify
from app.utils import safe_dict, roles_required, handle_db_error, generate_sequential_id
from app.services import UserService
from app.services.pt_service import PTService
from app.database import get_db_context
from datetime import datetime

trainer_bp = Blueprint('trainer_bp', __name__)


# ─── TRAINERS (Users với role=PT) ────────────────────────────────────────────

@trainer_bp.route('/api/trainers', methods=['GET'])
@roles_required('ADMIN')
def get_trainers():
    try:
        with get_db_context() as (conn, cur):
            cur.execute(
                "SELECT id, username, fullName, role, specialty, phone, address, activeStudents FROM Users WHERE role='PT' ORDER BY fullName"
            )
            return jsonify({'success': True, 'data': [safe_dict(r) for r in cur.fetchall()]})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 500


@trainer_bp.route('/api/trainers', methods=['POST'])
@roles_required('ADMIN')
def add_trainer():
    """Thêm HLV mới (tạo User với role=PT)"""
    try:
        data = request.json
        if not data.get('username'):
            return jsonify({'success': False, 'error': 'Tên đăng nhập không được để trống'}), 400
        if not data.get('password'):
            return jsonify({'success': False, 'error': 'Mật khẩu không được để trống'}), 400
        data['role'] = 'PT'
        UserService.them(data)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 400


@trainer_bp.route('/api/trainers/<id>', methods=['PUT'])
@roles_required('ADMIN')
def update_trainer(id):
    """Sửa thông tin HLV"""
    try:
        data = request.json
        data['role'] = 'PT'
        UserService.sua(id, data)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 400


@trainer_bp.route('/api/trainers/<id>', methods=['DELETE'])
@roles_required('ADMIN')
def delete_trainer(id):
    """Xóa HLV (kiểm tra FK trước)"""
    try:
        with get_db_context() as (conn, cur):
            # Kiểm tra có lớp đang dạy không
            cur.execute("SELECT COUNT(*) as c FROM Classes WHERE trainerId=%s AND status='ACTIVE'", (id,))
            if cur.fetchone()['c'] > 0:
                return jsonify({'success': False, 'error': 'Không thể xóa HLV đang có lớp học ACTIVE'}), 400
            UserService.xoa(id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 500


# ─── TRAINER ATTENDANCE ───────────────────────────────────────────────────────

@trainer_bp.route('/api/trainer-attendance', methods=['GET'])
@roles_required('ADMIN')
def get_trainer_attendance():
    try:
        # Sync absences first before fetching
        PTService.sync_absences()
        
        month = request.args.get('month', datetime.now().month)
        year = request.args.get('year', datetime.now().year)
        date_str = request.args.get('date')
        
        with get_db_context() as (conn, cur):
            sql = """SELECT ta.*, u.fullName as trainerName, c.name as className
                     FROM TrainerAttendance ta
                     JOIN Users u ON ta.trainerId=u.id
                     LEFT JOIN Classes c ON ta.classId=c.id
                     WHERE """
            params = []
            if date_str:
                sql += "ta.attendanceDate = %s "
                params.append(date_str)
            else:
                sql += "MONTH(ta.attendanceDate)=%s AND YEAR(ta.attendanceDate)=%s "
                params.extend([month, year])
                
            sql += "ORDER BY ta.attendanceDate DESC"
            cur.execute(sql, tuple(params))
            return jsonify({'success': True, 'data': [safe_dict(r) for r in cur.fetchall()]})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 500


@trainer_bp.route('/api/trainer-attendance', methods=['POST'])
@roles_required('ADMIN')
def add_attendance():
    try:
        data = request.json
        trainer_id = data.get('trainerId')
        att_date = data.get('attendanceDate')

        with get_db_context() as (conn, cur):
            # Check if locked
            if att_date:
                dt = datetime.strptime(att_date, '%Y-%m-%d')
                cur.execute("SELECT id FROM TrainerSalaries WHERE trainerId=%s AND month=%s AND year=%s AND paymentStatus='PAID'", (trainer_id, dt.month, dt.year))
                if cur.fetchone():
                    return jsonify({'success': False, 'error': 'Không thể thêm chấm công cho tháng đã thanh toán lương (đã khóa)'}), 400

            # Tự động tính số buổi dạy trong ngày đó nếu không nhập
            sessions = data.get('sessionsCount')
            if not sessions or int(sessions) == 0:
                try:
                    dt = datetime.strptime(att_date, '%Y-%m-%d')
                    days_map = {0: 'Thứ 2', 1: 'Thứ 3', 2: 'Thứ 4', 3: 'Thứ 5', 4: 'Thứ 6', 5: 'Thứ 7', 6: 'Chủ nhật'}
                    day_name = days_map[dt.weekday()]
                    cur.execute(
                        "SELECT COUNT(*) as c FROM Classes WHERE trainerId=%s AND dayOfWeek LIKE %s AND status='ACTIVE'",
                        (trainer_id, f"%{day_name}%")
                    )
                    sessions = cur.fetchone()['c'] or 1
                except Exception:
                    sessions = 1

            cur.execute(
                """INSERT INTO TrainerAttendance
                   (id, trainerId, classId, attendanceDate, checkIn, checkOut, status, sessionsCount, note)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (generate_sequential_id('TrainerAttendance', 'TA'), trainer_id, data.get('classId'), att_date,
                 data.get('checkIn'), data.get('checkOut'),
                 data.get('status', 'PRESENT'), int(sessions), data.get('note'))
            )
            conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 500


@trainer_bp.route('/api/trainer-attendance/<id>', methods=['PUT'])
@roles_required('ADMIN')
def update_attendance(id):
    """Sửa bản ghi chấm công"""
    try:
        data = request.json
        with get_db_context() as (conn, cur):
            # Check if locked
            cur.execute("SELECT trainerId, attendanceDate FROM TrainerAttendance WHERE id=%s", (id,))
            record = cur.fetchone()
            if not record:
                return jsonify({'success': False, 'error': 'Không tìm thấy bản ghi'}), 404
                
            att_date = record['attendanceDate']
            cur.execute("SELECT id FROM TrainerSalaries WHERE trainerId=%s AND month=%s AND year=%s AND paymentStatus='PAID'", (record['trainerId'], att_date.month, att_date.year))
            if cur.fetchone():
                return jsonify({'success': False, 'error': 'Không thể sửa chấm công của tháng đã thanh toán lương (đã khóa)'}), 400
                
            # Cập nhật
            cur.execute(
                """UPDATE TrainerAttendance 
                   SET classId=%s, attendanceDate=%s, checkIn=%s, checkOut=%s, status=%s, sessionsCount=%s, note=%s
                   WHERE id=%s""",
                (data.get('classId'), data.get('attendanceDate'), data.get('checkIn'), data.get('checkOut'),
                 data.get('status'), data.get('sessionsCount'), data.get('note'), id)
            )
            conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 500


# ─── TRAINER PAYROLL ─────────────────────────────────────────────────────────

@trainer_bp.route('/api/trainer-payroll', methods=['GET'])
@roles_required('ADMIN')
def get_payroll():
    """Tổng hợp lương dự kiến theo tháng (tính từ attendance)"""
    try:
        month = request.args.get('month', datetime.now().month)
        year = request.args.get('year', datetime.now().year)
        with get_db_context() as (conn, cur):
            cur.execute("SELECT id, fullName, specialty FROM Users WHERE role='PT'")
            trainers = cur.fetchall()
            payroll = []
            for t in trainers:
                tid = t['id']
                cur.execute(
                    "SELECT SUM(sessionsCount) as s FROM TrainerAttendance WHERE trainerId=%s AND MONTH(attendanceDate)=%s AND YEAR(attendanceDate)=%s",
                    (tid, month, year)
                )
                sessions = cur.fetchone()['s'] or 0
                cur.execute("SELECT COUNT(*) as c FROM Members WHERE assignedPTId=%s AND status='ACTIVE'", (tid,))
                students = cur.fetchone()['c']
                cur.execute("SELECT COUNT(*) as c FROM Classes WHERE trainerId=%s AND status='ACTIVE'", (tid,))
                classes = cur.fetchone()['c']
                salary = int(sessions) * 200000 + students * 50000
                payroll.append({
                    'trainerId': tid, 'trainerName': t['fullName'], 'specialty': t['specialty'],
                    'sessions': int(sessions), 'students': students, 'classes': classes,
                    'totalSalary': salary
                })
            return jsonify({'success': True, 'data': payroll})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 500


# ─── TRAINER SALARY ───────────────────────────────────────────────────────────

@trainer_bp.route('/api/trainer-salary', methods=['GET'])
@roles_required('ADMIN')
def get_salaries():
    try:
        month = request.args.get('month', datetime.now().month)
        year = request.args.get('year', datetime.now().year)
        with get_db_context() as (conn, cur):
            sql = """SELECT ts.*, u.fullName as trainerName, u.specialty
                     FROM TrainerSalaries ts
                     JOIN Users u ON ts.trainerId = u.id
                     WHERE ts.month = %s AND ts.year = %s
                     ORDER BY u.fullName"""
            cur.execute(sql, (month, year))
            return jsonify({'success': True, 'data': [safe_dict(r) for r in cur.fetchall()]})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 500


@trainer_bp.route('/api/trainer-salary/calculate', methods=['POST'])
@roles_required('ADMIN')
def calculate_salaries():
    """Tính lương tự động cho tất cả HLV trong tháng"""
    try:
        data = request.json
        month = int(data.get('month'))
        year = int(data.get('year'))
        base_salary = float(data.get('baseSalary', 5000000))
        bonus_per_session = float(data.get('bonusPerSession', 150000))

        with get_db_context() as (conn, cur):
            cur.execute("SELECT id FROM Users WHERE role='PT'")
            trainers = cur.fetchall()
            for t in trainers:
                tid = t['id']
                cur.execute(
                    "SELECT SUM(sessionsCount) as s FROM TrainerAttendance WHERE trainerId=%s AND MONTH(attendanceDate)=%s AND YEAR(attendanceDate)=%s",
                    (tid, month, year)
                )
                sessions = cur.fetchone()['s'] or 0
                session_bonus = float(sessions) * bonus_per_session

                # Upsert bản ghi lương
                cur.execute(
                    "SELECT id, bonus, deductions, paymentStatus FROM TrainerSalaries WHERE trainerId=%s AND month=%s AND year=%s",
                    (tid, month, year)
                )
                existing = cur.fetchone()
                
                # Bỏ qua nếu đã thanh toán
                if existing and existing['paymentStatus'] == 'PAID':
                    continue
                    
                bonus = float(existing['bonus']) if existing else 0.0
                deductions = float(existing['deductions']) if existing else 0.0
                total_amount = base_salary + session_bonus + bonus - deductions

                if existing:
                    cur.execute(
                        "UPDATE TrainerSalaries SET baseSalary=%s, totalSessions=%s, sessionBonus=%s, totalAmount=%s WHERE id=%s",
                        (base_salary, int(sessions), session_bonus, total_amount, existing['id'])
                    )
                else:
                    cur.execute(
                        """INSERT INTO TrainerSalaries (id, trainerId, month, year, baseSalary, totalSessions, sessionBonus, bonus, deductions, totalAmount)
                           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                        (generate_sequential_id('TrainerSalaries', 'TS'), tid, month, year, base_salary, int(sessions), session_bonus, bonus, deductions, total_amount)
                    )
            conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 500

@trainer_bp.route('/api/trainer-salary/<id>', methods=['PUT'])
@roles_required('ADMIN')
def update_salary(id):
    """Cập nhật Thưởng và Khấu trừ cho 1 bản ghi lương"""
    try:
        data = request.json
        bonus = float(data.get('bonus', 0))
        deductions = float(data.get('deductions', 0))
        
        with get_db_context() as (conn, cur):
            cur.execute("SELECT baseSalary, sessionBonus, paymentStatus FROM TrainerSalaries WHERE id=%s", (id,))
            record = cur.fetchone()
            if not record:
                return jsonify({'success': False, 'error': 'Không tìm thấy bản ghi lương'}), 404
            
            if record['paymentStatus'] == 'PAID':
                return jsonify({'success': False, 'error': 'Không thể sửa lương đã thanh toán'}), 400
                
            total_amount = float(record['baseSalary']) + float(record['sessionBonus']) + bonus - deductions
            
            cur.execute(
                "UPDATE TrainerSalaries SET bonus=%s, deductions=%s, totalAmount=%s WHERE id=%s",
                (bonus, deductions, total_amount, id)
            )
            conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 500


@trainer_bp.route('/api/trainer-salary/<id>/pay', methods=['PUT'])
@roles_required('ADMIN')
def pay_salary(id):
    """Đánh dấu đã thanh toán lương"""
    try:
        with get_db_context() as (conn, cur):
            cur.execute(
                "UPDATE TrainerSalaries SET paymentStatus='PAID', paidDate=%s WHERE id=%s",
                (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), id)
            )
            conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 500
