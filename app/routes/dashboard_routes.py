from flask import Blueprint, request, jsonify
from app.utils import safe_dict, roles_required, handle_db_error
from app.database import get_db_context
from datetime import datetime
import uuid

dashboard_bp = Blueprint('dashboard_bp', __name__)

@dashboard_bp.route('/api/checkins', methods=['GET'])
@roles_required('ADMIN', 'PT')
def get_checkins():
    try:
        date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        with get_db_context() as (conn, cur):
            sql = """SELECT c.*, m.fullName, m.phone 
                     FROM CheckIns c 
                     JOIN Members m ON c.memberId = m.id 
                     WHERE DATE(c.checkInTime) = %s 
                     ORDER BY c.checkInTime DESC"""
            cur.execute(sql, (date,))
            return jsonify({'success': True, 'data': [safe_dict(r) for r in cur.fetchall()]})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 500

@dashboard_bp.route('/api/checkins', methods=['POST'])
@roles_required('ADMIN', 'PT')
def do_checkin():
    try:
        data = request.json
        member_id = data.get('memberId')
        
        with get_db_context() as (conn, cur):
            # 1. Check Card Status
            cur.execute("SELECT status, expiryDate FROM MemberCards WHERE memberId=%s AND status='ACTIVE' ORDER BY expiryDate DESC LIMIT 1", (member_id,))
            card = cur.fetchone()
            if not card:
                return jsonify({'success': False, 'error': 'Hội viên không có thẻ ACTIVE'}), 400
            
            if datetime.strptime(str(card['expiryDate']), '%Y-%m-%d') < datetime.now():
                return jsonify({'success': False, 'error': 'Thẻ hội viên đã hết hạn'}), 400

            # 2. Check for unpaid PLAN invoices
            cur.execute("SELECT COUNT(*) as c FROM Invoices WHERE memberId=%s AND sourceType='PLAN' AND paymentStatus != 'PAID'", (member_id,))
            if cur.fetchone()['c'] > 0:
                return jsonify({'success': False, 'error': 'Hội viên còn hóa đơn gói tập chưa thanh toán'}), 400

            # 3. Perform Check-in
            cid = str(uuid.uuid4())[:8]
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cur.execute("INSERT INTO CheckIns (id, memberId, checkInTime, checkType, note) VALUES (%s, %s, %s, %s, %s)",
                        (cid, member_id, now, data.get('checkType', 'MANUAL'), data.get('note')))
            conn.commit()
            return jsonify({'success': True, 'checkInTime': now})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 500

@dashboard_bp.route('/api/checkins/<id>/checkout', methods=['PUT'])
@roles_required('ADMIN', 'PT')
def do_checkout(id):
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with get_db_context() as (conn, cur):
            cur.execute("UPDATE CheckIns SET checkOutTime=%s WHERE id=%s", (now, id))
            conn.commit()
        return jsonify({'success': True, 'checkOutTime': now})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 500

@dashboard_bp.route('/api/dashboard/stats', methods=['GET'])
@roles_required('ADMIN', 'PT')
def get_dashboard_stats():
    try:
        with get_db_context() as (conn, cur):
            # Members stats
            cur.execute("SELECT COUNT(*) as total FROM Members")
            total_members = cur.fetchone()['total']
            
            cur.execute("SELECT COUNT(*) as active FROM Members WHERE status='ACTIVE'")
            active_members = cur.fetchone()['active']
            
            # Revenue stats (standardized columns)
            cur.execute("SELECT SUM(paidAmount) as revenue FROM Invoices WHERE paymentStatus != 'CANCELLED'")
            total_revenue = cur.fetchone()['revenue'] or 0
            
            # Unpaid invoices
            cur.execute("SELECT COUNT(*) as unpaid FROM Invoices WHERE paymentStatus != 'PAID' AND paymentStatus != 'CANCELLED'")
            unpaid_count = cur.fetchone()['unpaid']
            
            # Classes soon full
            cur.execute("""SELECT c.name, (SELECT COUNT(*) FROM ClassEnrollments WHERE classId=c.id) as enrolled, c.capacity 
                           FROM Classes c 
                           HAVING enrolled >= c.capacity * 0.8""")
            classes_full = cur.fetchall()

            return jsonify({
                'success': True,
                'stats': {
                    'totalMembers': total_members,
                    'activeMembers': active_members,
                    'totalRevenue': float(total_revenue),
                    'unpaidCount': unpaid_count,
                    'classesSoonFull': classes_full
                }
            })
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 500
