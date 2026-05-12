from flask import Blueprint, request, jsonify, session
from app.utils import safe_dict, login_required, roles_required, handle_db_error
from app.services import UserService

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    u, p = data.get('username'), data.get('password')
    user = UserService.dang_nhap(u, p)
    if user:
        if user.role not in ('ADMIN', 'PT'):
            return jsonify({'success': False, 'message': 'Tai khoan nay khong co quyen truy cap he thong quan ly'}), 403
        session['user'] = {'id': user.id, 'fullName': user.fullName, 'role': user.role}
        return jsonify({'success': True, 'user': session['user']})
    return jsonify({'success': False, 'message': 'Sai ten dang nhap hoac mat khau'}), 401

@auth_bp.route('/auth/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({'success': True})

@auth_bp.route('/auth/me', methods=['GET'])
@login_required
def me():
    return jsonify({'success': True, 'user': session['user']})
