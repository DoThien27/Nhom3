from flask import Blueprint, request, jsonify
from app.utils import safe_dict, roles_required, handle_db_error
from app.services import EventService
from app.models import SuKien
from app.database import get_db_context
import uuid
from datetime import datetime

event_bp = Blueprint('event_bp', __name__)

@event_bp.route('/api/events', methods=['GET'])
@roles_required('ADMIN', 'PT')
def get_events():
    try:
        data = EventService.lay_tat_ca()
        return jsonify({'success': True, 'data': [safe_dict(e) for e in data]})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 500

@event_bp.route('/api/events/<event_id>/register', methods=['POST'])
@roles_required('ADMIN', 'PT')
def register_participant(event_id):
    try:
        member_id = request.json.get('member_id')
        member_name = request.json.get('member_name', '')
        
        with get_db_context() as (conn, cur):
            # 1. Check Capacity
            cur.execute("SELECT capacity, price, name FROM Events WHERE id=%s", (event_id,))
            evt = cur.fetchone()
            cur.execute("SELECT COUNT(*) as c FROM EventParticipants WHERE eventId=%s", (event_id,))
            if cur.fetchone()['c'] >= evt['capacity']:
                return jsonify({'success': False, 'error': 'Sự kiện đã hết chỗ'}), 400
            
            # 2. Check for duplicate
            cur.execute("SELECT * FROM EventParticipants WHERE eventId=%s AND memberId=%s", (event_id, member_id))
            if cur.fetchone():
                return jsonify({'success': False, 'error': 'Hội viên đã đăng ký sự kiện này'}), 400

            # 3. Register
            p_id = str(uuid.uuid4())[:8]
            cur.execute("INSERT INTO EventParticipants (id, eventId, memberId, memberName, registerDate, status) VALUES (%s,%s,%s,%s,%s,%s)",
                        (p_id, event_id, member_id, member_name, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'PENDING'))

            # 4. Create Invoice if needed
            if float(evt['price'] or 0) > 0:
                inv_id = 'INV'+str(uuid.uuid4())[:8].upper()
                cur.execute("""INSERT INTO Invoices 
                    (id, memberId, sourceType, sourceId, totalAmount, discountAmount, finalAmount, paidAmount, remainingAmount, date, paymentMethod, paymentStatus, note) 
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (inv_id, member_id, 'EVENT', event_id, evt['price'], 0, evt['price'], 0, evt['price'], datetime.now().strftime('%Y-%m-%d'), 'CASH', 'UNPAID', f"Đăng ký sự kiện: {evt['name']}"))
            
            conn.commit()
        return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 500

@event_bp.route('/api/events/<event_id>/register/<member_id>', methods=['DELETE'])
@roles_required('ADMIN', 'PT')
def unregister_participant(event_id, member_id):
    try:
        with get_db_context() as (conn, cur):
            cur.execute("DELETE FROM EventParticipants WHERE eventId=%s AND memberId=%s", (event_id, member_id))
            # Cancel unpaid invoice
            cur.execute("UPDATE Invoices SET paymentStatus='CANCELLED' WHERE memberId=%s AND sourceId=%s AND sourceType='EVENT' AND paymentStatus='UNPAID'", (member_id, event_id))
            conn.commit()
        return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 500

@event_bp.route('/api/events', methods=['POST'])
@roles_required('ADMIN', 'PT')
def add_event():
    try:
        data = request.json
        e = SuKien(
            id=str(uuid.uuid4())[:8], ten=data.get('ten'), mo_ta=data.get('mo_ta'),
            ngay=data.get('ngay'), gio=data.get('gio'), dia_diem=data.get('dia_diem'),
            suc_chua=int(data.get('suc_chua', 100)), gia=float(data.get('gia', 0)),
            facility_id=data.get('facility_id'), trang_thai=data.get('trang_thai', 'UPCOMING')
        )
        EventService.them(e)
        return jsonify({'success': True, 'event': safe_dict(e)})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 400

@event_bp.route('/api/events/<id>', methods=['PUT'])
@roles_required('ADMIN', 'PT')
def update_event(id):
    try:
        data = request.json
        EventService.sua(
            id, data.get('ten'), data.get('mo_ta'), data.get('ngay'),
            data.get('gio'), data.get('dia_diem'), int(data.get('suc_chua', 100)),
            float(data.get('gia', 0)), data.get('facility_id'), data.get('trang_thai', 'UPCOMING')
        )
        return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 400

@event_bp.route('/api/events/<id>', methods=['DELETE'])
@roles_required('ADMIN')
def delete_event(id):
    try:
        EventService.xoa(id)
        return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 500
