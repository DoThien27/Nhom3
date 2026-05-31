"""
app/routes/dashboard_routes.py
───────────────────────────────
Check-in / Check-out hội viên và thống kê dashboard.

Nghiệp vụ check-in:
1. Hội viên phải có thẻ ACTIVE và chưa hết hạn
2. Hội viên không được có hóa đơn gói tập UNPAID/PARTIAL
3. Hội viên không được đang trong CLB (đã checkin chưa checkout)
"""
from flask import Blueprint, request, jsonify
from app.utils import safe_dict, roles_required, handle_db_error
from app.database import get_db_context
from datetime import datetime, timedelta
from app.utils import generate_sequential_id

dashboard_bp = Blueprint('dashboard_bp', __name__)


# ─── CHECK-IN ─────────────────────────────────────────────────────────────────

@dashboard_bp.route('/api/checkins', methods=['GET'])
@roles_required('ADMIN')
def get_checkins():
    """Danh sách check-in theo ngày"""
    try:
        date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        with get_db_context() as (conn, cur):
            sql = """SELECT c.*, m.fullName, m.phone,
                            mc.cardNumber
                     FROM CheckIns c
                     JOIN Members m ON c.memberId = m.id
                     LEFT JOIN MemberCards mc ON c.cardId = mc.id
                     WHERE DATE(c.checkInTime) = %s
                     ORDER BY c.checkInTime DESC"""
            cur.execute(sql, (date,))
            return jsonify({'success': True, 'data': [safe_dict(r) for r in cur.fetchall()]})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 500


@dashboard_bp.route('/api/checkins', methods=['POST'])
@roles_required('ADMIN')
def do_checkin():
    """
    Check-in hội viên vào CLB.
    Các điều kiện:
    1. Phải có thẻ ACTIVE, chưa hết hạn
    2. Không có hóa đơn gói tập UNPAID/PARTIAL
    3. Chưa đang trong CLB (checkin chưa checkout)
    """
    try:
        data = request.json
        member_id = data.get('memberId')
        if not member_id:
            return jsonify({'success': False, 'error': 'Vui lòng chọn hội viên'}), 400

        with get_db_context() as (conn, cur):
            # 1. Kiểm tra thẻ ACTIVE và chưa hết hạn
            cur.execute(
                "SELECT id, status, expiryDate FROM MemberCards WHERE memberId=%s AND status='ACTIVE' ORDER BY expiryDate DESC LIMIT 1",
                (member_id,)
            )
            card = cur.fetchone()
            if not card:
                return jsonify({'success': False, 'error': 'Hội viên không có thẻ ACTIVE. Vui lòng cấp thẻ trước.'}), 400

            try:
                expiry_str = str(card['expiryDate'])[:10]
                expiry_date = datetime.strptime(expiry_str, '%Y-%m-%d')
                if expiry_date < datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
                    return jsonify({'success': False, 'error': 'Thẻ hội viên đã hết hạn'}), 400
            except Exception:
                pass  # Bỏ qua nếu parse ngày lỗi

            # 2. Kiểm tra hóa đơn gói tập chưa thanh toán
            cur.execute(
                "SELECT COUNT(*) as c FROM Invoices WHERE memberId=%s AND sourceType='PLAN' AND paymentStatus IN ('UNPAID','PARTIAL')",
                (member_id,)
            )
            if cur.fetchone()['c'] > 0:
                return jsonify({'success': False, 'error': 'Hội viên còn hóa đơn gói tập chưa thanh toán'}), 400

            # 3. Kiểm tra hội viên đang trong CLB (checkin chưa checkout)
            cur.execute(
                "SELECT id FROM CheckIns WHERE memberId=%s AND checkOutTime IS NULL AND DATE(checkInTime)=%s",
                (member_id, datetime.now().strftime('%Y-%m-%d'))
            )
            if cur.fetchone():
                return jsonify({'success': False, 'error': 'Hội viên đang trong CLB, chưa check-out'}), 400

            # 4. Thực hiện check-in
            cid = generate_sequential_id('CheckIns', 'CHK')
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cur.execute(
                "INSERT INTO CheckIns (id, memberId, cardId, checkInTime, checkType, note) VALUES (%s, %s, %s, %s, %s, %s)",
                (cid, member_id, card['id'], now, data.get('checkType', 'MANUAL'), data.get('note'))
            )
            conn.commit()
            return jsonify({'success': True, 'checkInTime': now, 'checkInId': cid})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 500


@dashboard_bp.route('/api/checkins/<id>/checkout', methods=['PUT'])
@roles_required('ADMIN')
def do_checkout(id):
    """Check-out hội viên khỏi CLB"""
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with get_db_context() as (conn, cur):
            cur.execute("UPDATE CheckIns SET checkOutTime=%s WHERE id=%s", (now, id))
            conn.commit()
        return jsonify({'success': True, 'checkOutTime': now})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 500


@dashboard_bp.route('/api/checkins/<id>', methods=['DELETE'])
@roles_required('ADMIN')
def delete_checkin(id):
    """Xóa bản ghi check-in"""
    try:
        with get_db_context() as (conn, cur):
            cur.execute("DELETE FROM CheckIns WHERE id=%s", (id,))
            conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 500


@dashboard_bp.route('/api/checkins/stats', methods=['GET'])
@roles_required('ADMIN')
def get_checkin_stats():
    """
    Thống kê check-in:
    - today: số lượt hôm nay
    - inside: số đang trong CLB (chưa checkout)
    - by_day: số lượt 7 ngày gần nhất
    """
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        with get_db_context() as (conn, cur):
            # Tổng lượt hôm nay
            cur.execute("SELECT COUNT(*) as c FROM CheckIns WHERE DATE(checkInTime)=%s", (today,))
            today_count = cur.fetchone()['c'] or 0

            # Số đang trong CLB (checkin hôm nay chưa checkout)
            cur.execute(
                "SELECT COUNT(*) as c FROM CheckIns WHERE DATE(checkInTime)=%s AND checkOutTime IS NULL",
                (today,)
            )
            inside_count = cur.fetchone()['c'] or 0

            # Số lượt 7 ngày gần nhất
            seven_days = []
            for i in range(6, -1, -1):
                d = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
                cur.execute("SELECT COUNT(*) as c FROM CheckIns WHERE DATE(checkInTime)=%s", (d,))
                count = cur.fetchone()['c'] or 0
                seven_days.append({'date': d, 'luot': count})

            return jsonify({
                'success': True,
                'data': {
                    'today': today_count,
                    'inside': inside_count,
                    'by_day': seven_days
                }
            })
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 500


# ─── DASHBOARD STATS ──────────────────────────────────────────────────────────

@dashboard_bp.route('/api/dashboard/stats', methods=['GET'])
@roles_required('ADMIN')
def get_dashboard_stats():
    """Số liệu tổng quan cho dashboard"""
    try:
        with get_db_context() as (conn, cur):
            # Tổng hội viên
            cur.execute("SELECT COUNT(*) as total FROM Members")
            total_members = cur.fetchone()['total'] or 0

            # Hội viên ACTIVE
            cur.execute("SELECT COUNT(*) as active FROM Members WHERE status='ACTIVE'")
            active_members = cur.fetchone()['active'] or 0

            # Tổng doanh thu (từ paidAmount)
            cur.execute(
                "SELECT COALESCE(SUM(paidAmount), 0) as revenue FROM Invoices WHERE paymentStatus != 'CANCELLED'"
            )
            total_revenue = cur.fetchone()['revenue'] or 0

            # Số hóa đơn chưa thanh toán
            cur.execute(
                "SELECT COUNT(*) as unpaid FROM Invoices WHERE paymentStatus IN ('UNPAID','PARTIAL')"
            )
            unpaid_count = cur.fetchone()['unpaid'] or 0

            # Lớp học sắp đầy (đã đăng ký >= 80% sức chứa)
            cur.execute("""
                SELECT c.name,
                       (SELECT COUNT(*) FROM ClassEnrollments WHERE classId=c.id) as enrolled,
                       c.capacity
                FROM Classes c
                WHERE c.status = 'ACTIVE'
                HAVING enrolled >= c.capacity * 0.8
            """)
            classes_full = [safe_dict(r) for r in cur.fetchall()]

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
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 500
