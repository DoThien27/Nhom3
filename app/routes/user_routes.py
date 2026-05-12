from flask import Blueprint, request, jsonify
from app.utils import safe_dict, roles_required, handle_db_error
from app.services import UserService
from app.database import get_db_context

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/api/users', methods=['GET'])
@roles_required('ADMIN')
def get_users():
    try:
        data = UserService.lay_tat_ca()
        return jsonify({'success': True, 'data': [safe_dict(r) for r in data]})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 500

@user_bp.route('/api/users', methods=['POST'])
@roles_required('ADMIN')
def add_user():
    try:
        data = request.json
        UserService.them(data)
        return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 500

@user_bp.route('/api/users/<id>', methods=['PUT'])
@roles_required('ADMIN')
def update_user(id):
    try:
        data = request.json
        UserService.sua(id, data)
        return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 500

@user_bp.route('/api/users/<id>', methods=['DELETE'])
@roles_required('ADMIN')
def delete_user(id):
    try:
        UserService.xoa(id)
        return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 500
