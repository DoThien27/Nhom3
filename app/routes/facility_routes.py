"""
app/routes/facility_routes.py
──────────────────────────────
API cho môn thể thao và cơ sở vật chất.

Fix: Frontend gửi 'name' nhưng service nhận 'sport_name'/'facility_name'.
Sửa bằng cách map trường trong route trước khi gọi service.
"""
from flask import Blueprint, request, jsonify
from app.utils import safe_dict, roles_required, handle_db_error
from app.services import SportService, FacilityService

facility_bp = Blueprint('facility_bp', __name__)


# ─── SPORTS ──────────────────────────────────────────────────────────────────

@facility_bp.route('/api/sports', methods=['GET'])
@roles_required('ADMIN')
def get_sports():
    try:
        data = SportService.lay_tat_ca()
        return jsonify({'success': True, 'data': [safe_dict(s) for s in data]})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 500


@facility_bp.route('/api/sports', methods=['POST'])
@roles_required('ADMIN')
def add_sport():
    """Frontend gửi {name, description} → map sang sport_name"""
    try:
        data = request.json
        # Nhận cả 'name' lẫn 'sport_name' để tương thích
        sport_name = data.get('sport_name') or data.get('name')
        description = data.get('description')
        if not sport_name:
            return jsonify({'success': False, 'error': 'Tên môn thể thao không được để trống'}), 400
        sport_id = SportService.them(sport_name, description)
        return jsonify({'success': True, 'id': sport_id})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 400


@facility_bp.route('/api/sports/<id>', methods=['PUT'])
@roles_required('ADMIN')
def update_sport(id):
    """Frontend gửi {name, description} → map sang sport_name"""
    try:
        data = request.json
        sport_name = data.get('sport_name') or data.get('name')
        description = data.get('description')
        SportService.sua(id, sport_name, description)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 400


@facility_bp.route('/api/sports/<id>', methods=['DELETE'])
@roles_required('ADMIN')
def delete_sport(id):
    try:
        SportService.xoa(id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 500


# ─── FACILITIES ───────────────────────────────────────────────────────────────

@facility_bp.route('/api/facilities', methods=['GET'])
@roles_required('ADMIN')
def get_facilities():
    try:
        data = FacilityService.lay_tat_ca()
        return jsonify({'success': True, 'data': [safe_dict(f) for f in data]})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 500


@facility_bp.route('/api/facilities', methods=['POST'])
@roles_required('ADMIN')
def add_facility():
    """Frontend gửi {name, location} → map sang facility_name"""
    try:
        data = request.json
        # Nhận cả 'name' lẫn 'facility_name' để tương thích
        facility_name = data.get('facility_name') or data.get('name')
        location = data.get('location')
        sport_id = data.get('sport_id')
        if not facility_name:
            return jsonify({'success': False, 'error': 'Tên cơ sở không được để trống'}), 400
        fid = FacilityService.them(facility_name, location, sport_id)
        return jsonify({'success': True, 'id': fid})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 400


@facility_bp.route('/api/facilities/<id>', methods=['PUT'])
@roles_required('ADMIN')
def update_facility(id):
    """Frontend gửi {name, location} → map sang facility_name"""
    try:
        data = request.json
        facility_name = data.get('facility_name') or data.get('name')
        location = data.get('location')
        sport_id = data.get('sport_id')
        FacilityService.sua(id, facility_name, location, sport_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 400


@facility_bp.route('/api/facilities/<id>', methods=['DELETE'])
@roles_required('ADMIN')
def delete_facility(id):
    try:
        FacilityService.xoa(id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 500
