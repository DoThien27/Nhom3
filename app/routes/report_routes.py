"""
app/routes/report_routes.py
────────────────────────────
Báo cáo thống kê.
Cho phép cả ADMIN và PT xem báo cáo (PT xem báo cáo giới hạn).
Menu frontend đã hiển thị 'reports' cho PT, backend cũng phải cho quyền.
"""
from flask import Blueprint, jsonify, request
from app.services.report_service import ReportService
from app.utils import roles_required, handle_db_error

report_bp = Blueprint('report_bp', __name__)


@report_bp.route('/api/reports', methods=['GET'])
@roles_required('ADMIN')
def get_reports():
    try:
        month = request.args.get('month')
        data = ReportService.get_full_report(month=month)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 500
