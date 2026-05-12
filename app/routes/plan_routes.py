from flask import Blueprint, request, jsonify
from app.utils import safe_dict, roles_required, handle_db_error
from app.services import PlanService
from app.models import GoiTap
import uuid

plan_bp = Blueprint('plan_bp', __name__)

@plan_bp.route('/api/plans', methods=['GET'])
@roles_required('ADMIN', 'PT')
def get_plans():
    try:
        data = PlanService.lay_tat_ca()
        return jsonify({'success': True, 'data': [safe_dict(p) for p in data]})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 500

@plan_bp.route('/api/plans', methods=['POST'])
@roles_required('ADMIN')
def add_plan():
    try:
        data = request.json
        p = GoiTap(
            id=str(uuid.uuid4())[:8],
            name=data.get('name'),
            type=data.get('type'),
            price=float(data.get('price', 0)),
            description=data.get('description'),
            durationMonths=int(data.get('durationMonths', 1))
        )
        PlanService.them(p)
        return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 400

@plan_bp.route('/api/plans/<id>', methods=['PUT'])
@roles_required('ADMIN')
def update_plan(id):
    try:
        data = request.json
        PlanService.sua(
            id, data.get('name'), data.get('type'), float(data.get('price', 0)),
            int(data.get('durationMonths', 1)), data.get('description')
        )
        return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 400

@plan_bp.route('/api/plans/<id>', methods=['DELETE'])
@roles_required('ADMIN')
def delete_plan(id):
    try:
        PlanService.xoa(id)
        return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 500
