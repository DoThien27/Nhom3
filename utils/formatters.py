"""
utils/formatters.py — Hàm tiện ích định dạng hiển thị
"""
from datetime import datetime, date as date_type


def format_currency(value) -> str:
    """300000 → '300.000đ'"""
    try:
        return f"{float(value):,.0f}đ".replace(",", ".")
    except (TypeError, ValueError):
        return "0đ"


def parse_currency(text: str) -> float:
    """'300.000' hoặc '300000' → 300000.0"""
    try:
        return float(str(text).replace(".", "").replace(",", "").replace("đ", "").strip())
    except (TypeError, ValueError):
        return 0.0


def format_date(value, fmt_out="%d/%m/%Y") -> str:
    """'2024-06-15' → '15/06/2024'"""
    if not value:
        return "---"
    try:
        if isinstance(value, (datetime, date_type)):
            return value.strftime(fmt_out)
        return datetime.strptime(str(value)[:10], "%Y-%m-%d").strftime(fmt_out)
    except ValueError:
        return str(value)


def translate_payment_status(status: str) -> str:
    MAP = {
        "UNPAID": "Chưa thanh toán",
        "PARTIAL": "Thanh toán một phần",
        "PAID": "Đã thanh toán",
        "CANCELLED": "Đã hủy",
    }
    return MAP.get(status, status or "---")


def translate_payment_method(method: str) -> str:
    MAP = {
        "CASH": "Tiền mặt",
        "BANK_TRANSFER": "Chuyển khoản",
        "CARD": "Thẻ",
        "E_WALLET": "Ví điện tử",
        "TRANSFER": "Chuyển khoản",
        "E-WALLET": "Ví điện tử",
        "OTHER": "Khác",
    }
    return MAP.get(method, method or "---")


def translate_item_type(item_type: str) -> str:
    MAP = {
        "MEMBERSHIP": "Gói hội viên",
        "CLASS":      "Lớp/Buổi tập",
        "FACILITY":   "Sân bãi/Phòng tập",
        "EVENT":      "Sự kiện/Giải đấu",
        "OTHER":      "Khác",
    }
    return MAP.get(item_type, item_type or "Khác")


PAYMENT_METHODS = ["CASH", "BANK_TRANSFER", "CARD", "E_WALLET", "OTHER"]
PAYMENT_METHODS_VI = [translate_payment_method(m) for m in PAYMENT_METHODS]

ITEM_TYPES = ["MEMBERSHIP", "CLASS", "FACILITY", "EVENT", "OTHER"]
ITEM_TYPES_VI = [translate_item_type(t) for t in ITEM_TYPES]

PAYMENT_STATUS_COLORS = {
    "UNPAID":    "#dc2626",
    "PARTIAL":   "#ea580c",
    "PAID":      "#059669",
    "CANCELLED": "#94a3b8",
}
