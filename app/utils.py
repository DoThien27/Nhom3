from flask import session, jsonify
from datetime import date, datetime
from decimal import Decimal
from functools import wraps

from dataclasses import is_dataclass, asdict

def safe_dict(row):
    """Convert DB row or dataclass to JSON-safe dict (handles Decimal, date, datetime)"""
    if is_dataclass(row):
        d = asdict(row)
    elif hasattr(row, '__dict__'):
        d = row.__dict__.copy()
    else:
        try:
            d = dict(row)
        except TypeError:
            d = row
    
    if isinstance(d, dict):
        for k, v in d.items():
            if isinstance(v, Decimal): d[k] = float(v)
            elif isinstance(v, (date, datetime)): d[k] = str(v)
    return d

def handle_db_error(e):
    err_str = str(e).lower()
    if "foreign key constraint fails" in err_str:
        return "Không thể xóa/sửa do dữ liệu này đang được liên kết (sử dụng) ở một chức năng khác."
    if "duplicate entry" in err_str:
        return "Dữ liệu này đã tồn tại trong hệ thống (trùng lặp)."
    if "data too long" in err_str:
        return "Dữ liệu nhập vào quá dài so với quy định."
    return str(e)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user' not in session:
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            if session['user']['role'] not in roles:
                return jsonify({'success': False, 'error': 'Permission denied'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator
