from flask import Blueprint, request, jsonify
from app.utils import safe_dict, roles_required, handle_db_error
from app.services import SportService, FacilityService

facility_bp = Blueprint('facility_bp', __name__)

@facility_bp.route('/api/sports', methods=['GET'])
@roles_required('ADMIN', 'PT')
def get_sports():
    try:
        data = SportService.lay_tat_ca()
        return jsonify({'success': True, 'data': [safe_dict(s) for s in data]})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 500

@facility_bp.route('/api/sports', methods=['POST'])
@roles_required('ADMIN')
def add_sport():
    try:
        data = request.json
        sport_id = SportService.them(data.get('sport_name'), data.get('description'))
        return jsonify({'success': True, 'id': sport_id})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 400

@facility_bp.route('/api/sports/<id>', methods=['PUT'])
@roles_required('ADMIN')
def update_sport(id):
    try:
        data = request.json
        SportService.sua(id, data.get('sport_name'), data.get('description'))
        return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 400

@facility_bp.route('/api/sports/<id>', methods=['DELETE'])
@roles_required('ADMIN')
def delete_sport(id):
    try:
        SportService.xoa(id)
        return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 500

@facility_bp.route('/api/facilities', methods=['GET'])
@roles_required('ADMIN', 'PT')
def get_facilities():
    try:
        data = FacilityService.lay_tat_ca()
        return jsonify({'success': True, 'data': [safe_dict(f) for f in data]})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 500

@facility_bp.route('/api/facilities', methods=['POST'])
@roles_required('ADMIN')
def add_facility():
    try:
        data = request.json
        fid = FacilityService.them(data.get('facility_name'), data.get('location'))
        return jsonify({'success': True, 'id': fid})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 400

@facility_bp.route('/api/facilities/<id>', methods=['PUT'])
@roles_required('ADMIN')
def update_facility(id):
    try:
        data = request.json
        FacilityService.sua(id, data.get('facility_name'), data.get('location'))
        return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 400

@facility_bp.route('/api/facilities/<id>', methods=['DELETE'])
@roles_required('ADMIN')
def delete_facility(id):
    try:
        FacilityService.xoa(id)
        return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 500
