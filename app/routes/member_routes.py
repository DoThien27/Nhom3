from flask import Blueprint, request, jsonify
from app.utils import safe_dict, roles_required, handle_db_error
from app.services import MemberService
from app.models import HoiVien
from app.database import get_db_context
import uuid
from datetime import datetime

member_bp = Blueprint('member_bp', __name__)

@member_bp.route('/api/members', methods=['GET'])
@roles_required('ADMIN', 'PT')
def get_members():
    try:
        data = MemberService.lay_tat_ca()
        return jsonify({'success': True, 'data': [safe_dict(hv) for hv in data]})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 500

@member_bp.route('/api/members', methods=['POST'])
@roles_required('ADMIN')
def add_member():
    try:
        data = request.json
        hv = HoiVien(
            id=str(uuid.uuid4())[:12],
            fullName=data.get('fullName'),
            phone=data.get('phone'),
            email=data.get('email'),
            joinDate=data.get('joinDate', datetime.now().strftime('%Y-%m-%d')),
            weight=float(data.get('weight', 0) or 0),
            assignedPTId=data.get('assignedPTId') or None,
            activePlanId=data.get('activePlanId') or None,
            username=data.get('username') or None,
            password=data.get('password') or None,
            homeTown=data.get('homeTown'),
            birthDate=data.get('birthDate'),
            gender=data.get('gender', 'Nam'),
            status=data.get('status', 'PENDING')
        )
        MemberService.them(hv)
        return jsonify({'success': True, 'member': safe_dict(hv)})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 400

@member_bp.route('/api/members/<id>', methods=['PUT'])
@roles_required('ADMIN')
def update_member(id):
    try:
        data = request.json
        hv = HoiVien(
            id=id,
            fullName=data.get('fullName'),
            phone=data.get('phone'),
            email=data.get('email'),
            weight=float(data.get('weight', 0) or 0),
            assignedPTId=data.get('assignedPTId') or None,
            activePlanId=data.get('activePlanId') or None,
            username=data.get('username') or None,
            password=data.get('password') or None,
            homeTown=data.get('homeTown'),
            birthDate=data.get('birthDate'),
            gender=data.get('gender', 'Nam'),
            status=data.get('status', 'PENDING')
        )
        MemberService.them(hv)
        return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 400

@member_bp.route('/api/members/<id>', methods=['DELETE'])
@roles_required('ADMIN')
def delete_member(id):
    try:
        MemberService.xoa(id)
        return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 500
