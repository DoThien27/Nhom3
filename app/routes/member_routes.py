"""
app/routes/member_routes.py
────────────────────────────
CRUD hội viên + Thẻ hội viên (MemberCards).
- Thêm mới: INSERT (không REPLACE INTO)
- Sửa: UPDATE (không mất FK liên quan)
- Thẻ: GET/POST/PUT/DELETE /api/member-cards
"""
from flask import Blueprint, request, jsonify
from app.utils import safe_dict, roles_required, handle_db_error
from app.services import MemberService
from app.models import HoiVien
from app.database import get_db_context
from app.utils import generate_sequential_id
from datetime import datetime

member_bp = Blueprint('member_bp', __name__)


# ─── MEMBERS ─────────────────────────────────────────────────────────────────

@member_bp.route('/api/members', methods=['GET'])
@roles_required('ADMIN')
def get_members():
    try:
        data = MemberService.lay_tat_ca()
        return jsonify({'success': True, 'data': [safe_dict(hv) for hv in data]})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 500


@member_bp.route('/api/members', methods=['POST'])
@roles_required('ADMIN')
def add_member():
    """Thêm mới hội viên - dùng INSERT"""
    try:
        data = request.json
        hv = HoiVien(
            id=generate_sequential_id('Members', 'MBR'),
            fullName=data.get('fullName'),
            phone=data.get('phone'),
            email=data.get('email'),
            joinDate=data.get('joinDate', datetime.now().strftime('%Y-%m-%d')),
            weight=float(data.get('weight', 0) or 0),
            previousWeight=float(data.get('previousWeight', 0) or 0),
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
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 400


@member_bp.route('/api/members/<id>', methods=['PUT'])
@roles_required('ADMIN')
def update_member(id):
    """Sửa thông tin hội viên - dùng UPDATE, không xóa FK"""
    try:
        data = request.json
        MemberService.cap_nhat(id, data)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 400


@member_bp.route('/api/members/<id>', methods=['DELETE'])
@roles_required('ADMIN')
def delete_member(id):
    try:
        MemberService.xoa(id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 500


@member_bp.route('/api/members/<id>/renew', methods=['POST'])
@roles_required('ADMIN')
def renew_member(id):
    """Gia hạn gói tập cho hội viên"""
    try:
        MemberService.gia_han(id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 400

@member_bp.route('/api/members/<id>/plan/register', methods=['POST'])
@roles_required('ADMIN')
def register_plan(id):
    try:
        MemberService.dang_ky_goi_tap(id, request.json.get('planId'))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 400

@member_bp.route('/api/members/<id>/plan/cancel', methods=['POST'])
@roles_required('ADMIN')
def cancel_plan(id):
    try:
        MemberService.huy_goi_tap(id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 400

@member_bp.route('/api/members/<id>/plan/change', methods=['POST'])
@roles_required('ADMIN')
def change_plan(id):
    try:
        MemberService.doi_goi_tap(id, request.json.get('planId'))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 400

# ─── MEMBER CARDS ─────────────────────────────────────────────────────────────

@member_bp.route('/api/member-cards', methods=['GET'])
@roles_required('ADMIN')
def get_member_cards():
    """Danh sách thẻ hội viên có kèm thông tin hội viên"""
    try:
        with get_db_context() as (conn, cur):
            sql = """SELECT mc.*, m.fullName, m.phone
                     FROM MemberCards mc
                     JOIN Members m ON mc.memberId = m.id
                     ORDER BY mc.createdAt DESC"""
            cur.execute(sql)
            return jsonify({'success': True, 'data': [safe_dict(r) for r in cur.fetchall()]})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 500


@member_bp.route('/api/member-cards', methods=['POST'])
@roles_required('ADMIN')
def issue_card():
    """
    Cấp thẻ mới cho hội viên.
    Yêu cầu: hội viên phải tồn tại.
    Thẻ sẽ ACTIVE ngay khi cấp thủ công (không qua gói tập).
    """
    try:
        data = request.json
        member_id = data.get('memberId')
        if not member_id:
            return jsonify({'success': False, 'error': 'Vui lòng chọn hội viên'}), 400

        with get_db_context() as (conn, cur):
            # Kiểm tra hội viên tồn tại
            cur.execute("SELECT id FROM Members WHERE id=%s", (member_id,))
            if not cur.fetchone():
                return jsonify({'success': False, 'error': 'Hội viên không tồn tại'}), 400

            card_id = generate_sequential_id('MemberCards', 'CRD')
            card_number = 'CARD' + card_id

            cur.execute(
                """INSERT INTO MemberCards (id, memberId, planId, cardNumber, issueDate, expiryDate, status, note)
                   VALUES (%s,%s,%s,%s,%s,%s,'ACTIVE',%s)""",
                (card_id, member_id, data.get('planId') or None, card_number,
                 data.get('issueDate') or datetime.now().strftime('%Y-%m-%d'),
                 data.get('expiryDate'),
                 data.get('note'))
            )
            cur.execute("UPDATE Members SET status='ACTIVE' WHERE id=%s", (member_id,))
            conn.commit()
            return jsonify({'success': True, 'cardNumber': card_number, 'cardId': card_id})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 400


@member_bp.route('/api/member-cards/<id>', methods=['PUT'])
@roles_required('ADMIN')
def update_card(id):
    """Cập nhật trạng thái thẻ (ví dụ: thu hồi → REVOKED)"""
    try:
        data = request.json
        new_status = data.get('status')
        with get_db_context() as (conn, cur):
            cur.execute("SELECT memberId FROM MemberCards WHERE id=%s", (id,))
            card = cur.fetchone()
            cur.execute("UPDATE MemberCards SET status=%s WHERE id=%s", (new_status, id))
            if card:
                member_id = card['memberId']
                cur.execute("SELECT COUNT(*) as c FROM MemberCards WHERE memberId=%s AND status='ACTIVE'", (member_id,))
                if cur.fetchone()['c'] > 0:
                    cur.execute("UPDATE Members SET status='ACTIVE' WHERE id=%s", (member_id,))
                else:
                    cur.execute("UPDATE Members SET status='INACTIVE' WHERE id=%s", (member_id,))
            conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 400


@member_bp.route('/api/member-cards/<id>', methods=['DELETE'])
@roles_required('ADMIN')
def delete_card(id):
    try:
        with get_db_context() as (conn, cur):
            cur.execute("SELECT memberId FROM MemberCards WHERE id=%s", (id,))
            card = cur.fetchone()
            cur.execute("DELETE FROM MemberCards WHERE id=%s", (id,))
            if card:
                member_id = card['memberId']
                cur.execute("SELECT COUNT(*) as c FROM MemberCards WHERE memberId=%s AND status='ACTIVE'", (member_id,))
                if cur.fetchone()['c'] == 0:
                    cur.execute("UPDATE Members SET status='INACTIVE' WHERE id=%s", (member_id,))
            conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 500
