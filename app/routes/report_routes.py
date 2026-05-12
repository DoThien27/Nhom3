from flask import Blueprint, jsonify
from app.services.report_service import ReportService
from app.utils import roles_required

report_bp = Blueprint('report_bp', __name__)

@report_bp.route('/api/reports', methods=['GET'])
@roles_required('ADMIN')
def get_reports():
    try:
        data = ReportService.get_full_report()
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
