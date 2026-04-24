from typing import List
from database.db_connection import get_connection
from models.models import Invoice, InvoiceItem


def get_all() -> List[Invoice]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Invoices")
    inv_rows = cur.fetchall()
    cur.execute("SELECT * FROM InvoiceItems")
    item_rows = cur.fetchall()

    invoices = []
    for row in inv_rows:
        items = [
            InvoiceItem(name=it.name, quantity=int(it.quantity), price=float(it.price))
            for it in item_rows if str(it.invoiceId) == str(row.id)
        ]
        invoices.append(Invoice(
            id=str(row.id),
            memberId=str(row.memberId),
            items=items,
            total=float(row.total),
            date=str(row.date) if row.date else "",
            method=row.method or "CASH",
        ))
    return invoices


def create(invoice: Invoice) -> Invoice:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO Invoices (id, memberId, total, date, method) VALUES (?,?,?,?,?)",
            invoice.id, invoice.memberId, invoice.total, invoice.date, invoice.method
        )
        for item in invoice.items:
            cur.execute(
                "INSERT INTO InvoiceItems (invoiceId, name, quantity, price) VALUES (?,?,?,?)",
                invoice.id, item.name, item.quantity, item.price
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    return invoice
