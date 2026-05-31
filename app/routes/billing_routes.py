"""
app/routes/billing_routes.py
──────────────────────────────
Quản lý hóa đơn và thanh toán.

Các API:
  GET  /api/billing         - danh sách hóa đơn
  POST /api/billing         - tạo hóa đơn thủ công
  POST /api/billing/<id>/pay - thanh toán hóa đơn (toàn phần hoặc một phần)
  DELETE /api/billing/<id>  - xóa hóa đơn

Trạng thái hóa đơn: UNPAID → PARTIAL → PAID
"""
from flask import Blueprint, request, jsonify
from app.utils import safe_dict, roles_required, handle_db_error
from app.services import InvoiceService
from app.models import HoaDon
from app.utils import generate_sequential_id
from datetime import datetime

billing_bp = Blueprint('billing_bp', __name__)


@billing_bp.route('/api/billing', methods=['GET'])
@roles_required('ADMIN')
def get_billing():
    try:
        month = request.args.get('month')
        data = InvoiceService.lay_tat_ca(month=month)
        return jsonify({'success': True, 'data': [safe_dict(i) for i in data]})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 500


@billing_bp.route('/api/billing/<id>/pay', methods=['POST'])
@roles_required('ADMIN')
def pay_invoice(id):
    """
    Thanh toán hóa đơn (hỗ trợ thanh toán một phần hoặc toàn bộ).
    Sau khi PAID + sourceType='PLAN': kích hoạt hội viên và thẻ.
    """
    try:
        data = request.json
        amount = float(data.get('amount', 0))
        if amount <= 0:
            return jsonify({'success': False, 'error': 'Số tiền thanh toán phải lớn hơn 0'}), 400
        method = data.get('method', 'CASH')
        note = data.get('note', '')
        InvoiceService.thanh_toan(id, amount, method, note)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 400


@billing_bp.route('/api/billing', methods=['POST'])
@roles_required('ADMIN')
def create_invoice():
    """Tạo hóa đơn thủ công"""
    try:
        data = request.json
        amount = float(data.get('totalAmount', 0))
        if not data.get('memberId'):
            return jsonify({'success': False, 'error': 'Vui lòng chọn hội viên'}), 400
        status = data.get('paymentStatus', 'UNPAID')
        inv = HoaDon(
            id=generate_sequential_id('Invoices', 'INV'),
            memberId=data.get('memberId'),
            sourceType=data.get('sourceType') or 'MANUAL',
            sourceId=data.get('sourceId'),
            totalAmount=amount,
            discountAmount=0,
            finalAmount=amount,
            paidAmount=0,
            remainingAmount=amount,
            date=datetime.now().strftime('%Y-%m-%d'),
            paymentMethod=data.get('paymentMethod', 'CASH'),
            paymentStatus='UNPAID',
            note=data.get('note')
        )
        InvoiceService.them(inv)
        if status == 'PAID' and amount > 0:
            InvoiceService.thanh_toan(inv.id, amount, data.get('paymentMethod', 'CASH'), data.get('note'))
        elif status == 'PAID':
            # If amount is 0, just update status
            from app.database import get_db_context
            with get_db_context() as (conn, cur):
                cur.execute("UPDATE Invoices SET paymentStatus='PAID' WHERE id=%s", (inv.id,))
                conn.commit()

        # Reload invoice for response
        return jsonify({'success': True, 'invoice': safe_dict(inv)})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 400


@billing_bp.route('/api/billing/<id>', methods=['DELETE'])
@roles_required('ADMIN')
def delete_invoice(id):
    try:
        from app.database import get_db_context
        with get_db_context() as (conn, cur):
            cur.execute("DELETE FROM Invoices WHERE id=%s", (id,))
            conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': handle_db_error(e)}), 500
