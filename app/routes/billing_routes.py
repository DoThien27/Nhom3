from flask import Blueprint, request, jsonify, session
from app.utils import safe_dict, roles_required, handle_db_error
from app.services import InvoiceService
from app.models import HoaDon
import uuid
from datetime import datetime

billing_bp = Blueprint('billing_bp', __name__)

@billing_bp.route('/api/billing', methods=['GET'])
@roles_required('ADMIN', 'PT')
def get_billing():
    try:
        data = InvoiceService.lay_tat_ca()
        return jsonify({'success': True, 'data': [safe_dict(i) for i in data]})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 500

@billing_bp.route('/api/billing/<id>/pay', methods=['POST'])
@roles_required('ADMIN', 'PT')
def pay_invoice(id):
    try:
        data = request.json
        amount = float(data.get('amount', 0))
        method = data.get('method', 'CASH')
        note = data.get('note', '')
        InvoiceService.thanh_toan(id, amount, method, note)
        return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 400

@billing_bp.route('/api/billing', methods=['POST'])
@roles_required('ADMIN', 'PT')
def create_invoice():
    try:
        data = request.json
        amount = float(data.get('totalAmount', 0))
        status = data.get('paymentStatus', 'UNPAID')
        inv = HoaDon(
            id='INV'+str(uuid.uuid4())[:8].upper(), 
            memberId=data.get('memberId'),
            sourceType=data.get('sourceType', 'OTHER'),
            sourceId=data.get('sourceId'),
            totalAmount=amount, 
            discountAmount=0, 
            finalAmount=amount,
            paidAmount=amount if status == 'PAID' else 0,
            remainingAmount=0 if status == 'PAID' else amount,
            date=datetime.now().strftime('%Y-%m-%d'), 
            paymentMethod=data.get('paymentMethod', 'CASH'),
            paymentStatus=status,
            note=data.get('note')
        )
        InvoiceService.them(inv)
        return jsonify({'success': True, 'invoice': safe_dict(inv)})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 400

@billing_bp.route('/api/billing/<id>', methods=['DELETE'])
@roles_required('ADMIN')
def delete_invoice(id):
    try:
        from app.database import get_db_context
        with get_db_context() as (conn, cur):
            cur.execute("DELETE FROM Invoices WHERE id=%s", (id,))
            conn.commit()
        return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'error': handle_db_error(e)}), 500
