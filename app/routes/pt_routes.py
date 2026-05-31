from flask import Blueprint, jsonify, request, session
from app.services.pt_service import PTService
from app.utils import roles_required, safe_dict, handle_db_error

pt_bp = Blueprint('pt_bp', __name__)

@pt_bp.route('/api/pt/profile', methods=['GET'])
@roles_required('PT')
def get_profile():
    try:
        user_id = session['user']['id']
        data = PTService.get_profile(user_id)
        return jsonify({'success': True, 'data': safe_dict(data)})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 500

@pt_bp.route('/api/pt/classes', methods=['GET'])
@roles_required('PT')
def get_classes():
    try:
        user_id = session['user']['id']
        data = PTService.get_my_classes(user_id)
        return jsonify({'success': True, 'data': [safe_dict(r) for r in data]})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 500

@pt_bp.route('/api/pt/classes/<class_id>/students', methods=['GET'])
@roles_required('PT')
def get_students(class_id):
    try:
        user_id = session['user']['id']
        data = PTService.get_class_students(user_id, class_id)
        return jsonify({'success': True, 'data': [safe_dict(r) for r in data]})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 500

@pt_bp.route('/api/pt/classes/<class_id>/attendance', methods=['GET', 'POST'])
@roles_required('PT')
def handle_attendance(class_id):
    try:
        user_id = session['user']['id']
        if request.method == 'POST':
            data = request.json
            date_str = data.get('date')
            attendance = data.get('attendance', [])
            if not date_str or not attendance:
                return jsonify({'success': False, 'error': 'Thiếu dữ liệu điểm danh'}), 400
            
            PTService.take_attendance(user_id, class_id, date_str, attendance)
            return jsonify({'success': True})
        else:
            date_str = request.args.get('date')
            data = PTService.get_attendance_history(user_id, class_id, date_str)
            return jsonify({'success': True, 'data': [safe_dict(r) for r in data]})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 500

@pt_bp.route('/api/pt/attendance', methods=['GET'])
@roles_required('PT')
def get_my_attendance():
    try:
        user_id = session['user']['id']
        data = PTService.get_my_attendance(user_id)
        return jsonify({'success': True, 'data': [safe_dict(r) for r in data]})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 500

@pt_bp.route('/api/pt/salary', methods=['GET'])
@roles_required('PT')
def get_my_salary():
    try:
        user_id = session['user']['id']
        data = PTService.get_my_salary(user_id)
        return jsonify({'success': True, 'data': [safe_dict(r) for r in data]})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 500

@pt_bp.route('/api/pt/today-shifts', methods=['GET'])
@roles_required('PT')
def get_today_shifts():
    try:
        user_id = session['user']['id']
        data = PTService.get_today_shifts(user_id)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 500

@pt_bp.route('/api/pt/checkin', methods=['POST'])
@roles_required('PT')
def pt_checkin():
    try:
        user_id = session['user']['id']
        data = request.json or {}
        class_id = data.get('classId')
        PTService.pt_check_in(user_id, class_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 500

@pt_bp.route('/api/pt/checkout', methods=['POST'])
@roles_required('PT')
def pt_checkout():
    try:
        user_id = session['user']['id']
        data = request.json or {}
        attendance_id = data.get('attendanceId')
        if not attendance_id:
            return jsonify({'success': False, 'error': 'Thiếu ID điểm danh'}), 400
        PTService.pt_check_out(user_id, attendance_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 500

