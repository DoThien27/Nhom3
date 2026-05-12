from flask import Blueprint, request, jsonify
from app.utils import safe_dict, roles_required, handle_db_error
from app.database import get_db_context
import uuid
from datetime import datetime

trainer_bp = Blueprint('trainer_bp', __name__)

@trainer_bp.route('/api/trainers', methods=['GET'])
@roles_required('ADMIN', 'PT')
def get_trainers():
    try:
        with get_db_context() as (conn, cur):
            cur.execute("SELECT * FROM Users WHERE role='PT'")
            return jsonify({'success': True, 'data': [safe_dict(r) for r in cur.fetchall()]})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 500

@trainer_bp.route('/api/trainer-attendance', methods=['GET'])
@roles_required('ADMIN', 'PT')
def get_trainer_attendance():
    try:
        month = request.args.get('month', datetime.now().month)
        year = request.args.get('year', datetime.now().year)
        with get_db_context() as (conn, cur):
            sql = """SELECT ta.*, u.fullName as trainerName 
                     FROM TrainerAttendance ta 
                     JOIN Users u ON ta.trainerId=u.id 
                     WHERE MONTH(ta.attendanceDate)=%s AND YEAR(ta.attendanceDate)=%s 
                     ORDER BY ta.attendanceDate DESC"""
            cur.execute(sql, (month, year))
            return jsonify({'success': True, 'data': [safe_dict(r) for r in cur.fetchall()]})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 500

@trainer_bp.route('/api/trainer-attendance', methods=['POST'])
@roles_required('ADMIN', 'PT')
def add_attendance():
    try:
        data = request.json
        trainer_id = data.get('trainerId')
        att_date = data.get('attendanceDate')
        
        with get_db_context() as (conn, cur):
            dt = datetime.strptime(att_date, '%Y-%m-%d')
            days = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]
            day_name = days[dt.weekday()]
            
            cur.execute("SELECT COUNT(*) as c FROM Classes WHERE trainerId=%s AND dayOfWeek LIKE %s", (trainer_id, f"%{day_name}%"))
            class_count = cur.fetchone()['c']
            
            sessions = data.get('sessionsCount')
            if not sessions or int(sessions) == 0:
                sessions = class_count

            cur.execute(
                "INSERT INTO TrainerAttendance (id, trainerId, attendanceDate, checkIn, checkOut, status, sessionsCount, note) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (str(uuid.uuid4())[:8], trainer_id, att_date, data.get('checkIn'), data.get('checkOut'), data.get('status'), sessions, data.get('note'))
            )
            conn.commit()
        return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 500

@trainer_bp.route('/api/trainer-payroll', methods=['GET'])
@roles_required('ADMIN')
def get_payroll():
    try:
        month = request.args.get('month', datetime.now().month)
        year = request.args.get('year', datetime.now().year)
        with get_db_context() as (conn, cur):
            cur.execute("SELECT id, fullName, specialty FROM Users WHERE role='PT'")
            trainers = cur.fetchall()
            payroll = []
            for t in trainers:
                tid = t['id']
                cur.execute("SELECT SUM(sessionsCount) as s FROM TrainerAttendance WHERE trainerId=%s AND MONTH(attendanceDate)=%s AND YEAR(attendanceDate)=%s", (tid, month, year))
                sessions = cur.fetchone()['s'] or 0
                cur.execute("SELECT COUNT(*) as c FROM Members WHERE assignedPTId=%s", (tid,))
                students = cur.fetchone()['c']
                cur.execute("SELECT COUNT(*) as c FROM Classes WHERE trainerId=%s", (tid,))
                classes = cur.fetchone()['c']
                salary = sessions * 200000 + students * 50000
                payroll.append({
                    'trainerId': tid, 'trainerName': t['fullName'], 'specialty': t['specialty'],
                    'sessions': int(sessions), 'students': students, 'classes': classes, 'totalSalary': salary
                })
            return jsonify({'success': True, 'data': payroll})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 500

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
                     WHERE ts.month = %s AND ts.year = %s"""
            cur.execute(sql, (month, year))
            return jsonify({'success': True, 'data': [safe_dict(r) for r in cur.fetchall()]})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 500

@trainer_bp.route('/api/trainer-salary/calculate', methods=['POST'])
@roles_required('ADMIN')
def calculate_salaries():
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
                cur.execute("SELECT SUM(sessionsCount) as s FROM TrainerAttendance WHERE trainerId=%s AND MONTH(attendanceDate)=%s AND YEAR(attendanceDate)=%s", (tid, month, year))
                sessions = cur.fetchone()['s'] or 0
                total_bonus = float(sessions) * bonus_per_session
                total_amount = base_salary + total_bonus
                
                # Upsert salary record
                cur.execute("SELECT id FROM TrainerSalaries WHERE trainerId=%s AND month=%s AND year=%s", (tid, month, year))
                existing = cur.fetchone()
                if existing:
                    cur.execute("UPDATE TrainerSalaries SET baseSalary=%s, totalSessions=%s, sessionBonus=%s, totalAmount=%s WHERE id=%s",
                                (base_salary, int(sessions), total_bonus, total_amount, existing['id']))
                else:
                    cur.execute("INSERT INTO TrainerSalaries (id, trainerId, month, year, baseSalary, totalSessions, sessionBonus, totalAmount) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                                (str(uuid.uuid4())[:8], tid, month, year, base_salary, int(sessions), total_bonus, total_amount))
            conn.commit()
        return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 500

@trainer_bp.route('/api/trainer-salary/<id>/pay', methods=['PUT'])
@roles_required('ADMIN')
def pay_salary(id):
    try:
        with get_db_context() as (conn, cur):
            cur.execute("UPDATE TrainerSalaries SET paymentStatus='PAID', paidDate=%s WHERE id=%s", (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), id))
            conn.commit()
        return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 500
