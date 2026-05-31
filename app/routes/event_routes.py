"""
app/routes/event_routes.py
───────────────────────────
Quản lý sự kiện và danh sách tham gia.

Endpoint tham gia đã đổi từ /register → /participants
để khớp với frontend gọi:
  GET  /api/events/<id>/participants
  POST /api/events/<id>/participants
  DELETE /api/events/<id>/participants/<memberId>

Nghiệp vụ:
- Không cho đăng ký vượt sức chứa
- Không cho đăng ký trùng
- Hủy đăng ký: xóa khỏi danh sách + hủy hóa đơn UNPAID liên quan
"""
from flask import Blueprint, request, jsonify
from app.utils import safe_dict, roles_required, handle_db_error
from app.services import EventService
from app.models import SuKien
from app.database import get_db_context
from app.utils import generate_sequential_id
from datetime import datetime

event_bp = Blueprint('event_bp', __name__)


# ─── EVENTS CRUD ──────────────────────────────────────────────────────────────

@event_bp.route('/api/events', methods=['GET'])
@roles_required('ADMIN')
def get_events():
    try:
        data = EventService.lay_tat_ca()
        return jsonify({'success': True, 'data': [safe_dict(e) for e in data]})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 500


@event_bp.route('/api/events', methods=['POST'])
@roles_required('ADMIN')
def add_event():
    try:
        data = request.json
        gio = data.get('gio')
        gio_ket_thuc = data.get('gio_ket_thuc')
        
        if gio and gio_ket_thuc and gio >= gio_ket_thuc:
            return jsonify({'success': False, 'error': 'Giờ kết thúc phải lớn hơn giờ bắt đầu'}), 400

        e = SuKien(
            id=generate_sequential_id('Events', 'EVT'),
            ten=data.get('ten'),
            mo_ta=data.get('mo_ta'),
            ngay=data.get('ngay'),
            gio=gio,
            gio_ket_thuc=gio_ket_thuc,
            dia_diem=data.get('dia_diem'),
            suc_chua=int(data.get('suc_chua', 100)),
            gia=float(data.get('gia', 0)),
            facility_id=data.get('facility_id'),
            trang_thai=data.get('trang_thai', 'UPCOMING')
        )
        EventService.them(e)
        return jsonify({'success': True, 'event': safe_dict(e)})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 400


@event_bp.route('/api/events/<id>', methods=['PUT'])
@roles_required('ADMIN')
def update_event(id):
    try:
        data = request.json
        gio = data.get('gio')
        gio_ket_thuc = data.get('gio_ket_thuc')
        
        if gio and gio_ket_thuc and gio >= gio_ket_thuc:
            return jsonify({'success': False, 'error': 'Giờ kết thúc phải lớn hơn giờ bắt đầu'}), 400

        EventService.sua(
            id, data.get('ten'), data.get('mo_ta'), data.get('ngay'),
            gio, gio_ket_thuc, data.get('dia_diem'),
            int(data.get('suc_chua', 100)),
            float(data.get('gia', 0)),
            data.get('facility_id'),
            data.get('trang_thai', 'UPCOMING')
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 400


@event_bp.route('/api/events/<id>', methods=['DELETE'])
@roles_required('ADMIN')
def delete_event(id):
    try:
        EventService.xoa(id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 500


# ─── EVENT PARTICIPANTS ───────────────────────────────────────────────────────

@event_bp.route('/api/events/<event_id>/participants', methods=['GET'])
@roles_required('ADMIN')
def get_participants(event_id):
    """Danh sách người tham gia sự kiện"""
    try:
        with get_db_context() as (conn, cur):
            sql = """SELECT ep.*, m.fullName, m.phone
                     FROM EventParticipants ep
                     JOIN Members m ON ep.memberId = m.id
                     WHERE ep.eventId = %s
                     ORDER BY ep.registerDate"""
            cur.execute(sql, (event_id,))
            return jsonify({'success': True, 'data': [safe_dict(r) for r in cur.fetchall()]})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 500


@event_bp.route('/api/events/<event_id>/participants', methods=['POST'])
@roles_required('ADMIN')
def register_participant(event_id):
    """
    Đăng ký hội viên vào sự kiện.
    - Không vượt sức chứa
    - Không đăng ký trùng
    - Nếu sự kiện có phí, tạo Invoice UNPAID
    """
    try:
        member_id = request.json.get('memberId')
        if not member_id:
            return jsonify({'success': False, 'error': 'Vui lòng cung cấp memberId'}), 400

        with get_db_context() as (conn, cur):
            # Kiểm tra sức chứa
            cur.execute("SELECT capacity, price, name FROM Events WHERE id=%s", (event_id,))
            evt = cur.fetchone()
            if not evt:
                return jsonify({'success': False, 'error': 'Sự kiện không tồn tại'}), 404

            cur.execute("SELECT COUNT(*) as c FROM EventParticipants WHERE eventId=%s", (event_id,))
            if cur.fetchone()['c'] >= evt['capacity']:
                return jsonify({'success': False, 'error': 'Sự kiện đã hết chỗ'}), 400

            # Kiểm tra trùng
            cur.execute(
                "SELECT id FROM EventParticipants WHERE eventId=%s AND memberId=%s",
                (event_id, member_id)
            )
            if cur.fetchone():
                return jsonify({'success': False, 'error': 'Hội viên đã đăng ký sự kiện này'}), 400

            # Lấy tên hội viên
            cur.execute("SELECT fullName FROM Members WHERE id=%s", (member_id,))
            member = cur.fetchone()
            member_name = member['fullName'] if member else ''

            # Đăng ký
            p_id = generate_sequential_id('EventParticipants', 'EP')
            status = 'CONFIRMED' if float(evt['price'] or 0) == 0 else 'PENDING'
            cur.execute(
                """INSERT INTO EventParticipants (id, eventId, memberId, memberName, registerDate, status)
                   VALUES (%s,%s,%s,%s,%s,%s)""",
                (p_id, event_id, member_id, member_name, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), status)
            )

            # Tạo hóa đơn nếu sự kiện có phí
            if float(evt['price'] or 0) > 0:
                inv_id = generate_sequential_id('Invoices', 'INV')
                cur.execute(
                    """INSERT INTO Invoices
                       (id, memberId, sourceType, sourceId, totalAmount, discountAmount, finalAmount,
                        paidAmount, remainingAmount, date, paymentMethod, paymentStatus, note)
                       VALUES (%s,%s,'EVENT',%s,%s,0,%s,0,%s,%s,'CASH','UNPAID',%s)""",
                    (inv_id, member_id, event_id,
                     evt['price'], evt['price'], evt['price'],
                     datetime.now().strftime('%Y-%m-%d'),
                     f"Đăng ký sự kiện: {evt['name']}")
                )

            conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 500


@event_bp.route('/api/events/<event_id>/participants/<member_id>', methods=['DELETE'])
@roles_required('ADMIN')
def unregister_participant(event_id, member_id):
    """Hủy đăng ký, đồng thời hủy hóa đơn UNPAID liên quan"""
    try:
        with get_db_context() as (conn, cur):
            cur.execute(
                "DELETE FROM EventParticipants WHERE eventId=%s AND memberId=%s",
                (event_id, member_id)
            )
            # Hủy hóa đơn chưa thanh toán
            cur.execute(
                "UPDATE Invoices SET paymentStatus='CANCELLED' WHERE memberId=%s AND sourceId=%s AND sourceType='EVENT' AND paymentStatus='UNPAID'",
                (member_id, event_id)
            )
            conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 500


# ─── Alias cũ (giữ để không break nếu có gọi cũ) ────────────────────────────
@event_bp.route('/api/events/<event_id>/register', methods=['POST'])
@roles_required('ADMIN')
def register_participant_alias(event_id):
    return register_participant(event_id)


@event_bp.route('/api/events/<event_id>/register/<member_id>', methods=['DELETE'])
@roles_required('ADMIN')
def unregister_participant_alias(event_id, member_id):
    return unregister_participant(event_id, member_id)
