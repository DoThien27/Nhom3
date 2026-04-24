from typing import List
from database.db_connection import get_connection
from models.models import Product


def get_all() -> List[Product]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Products")
    products = []
    for row in cur.fetchall():
        products.append(Product(
            id=str(row.id),
            name=row.name,
            category=row.category,
            price=float(row.price),
            stock=int(row.stock),
            minStockAlert=int(row.minStockAlert),
        ))
    return products


def add(product: Product) -> Product:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO Products (id, name, category, price, stock, minStockAlert) "
        "VALUES (?,?,?,?,?,?)",
        product.id, product.name, product.category,
        product.price, product.stock, product.minStockAlert
    )
    conn.commit()
    return product


def update(product: Product) -> Product:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE Products SET name=?, category=?, price=?, stock=?, minStockAlert=? "
        "WHERE id=?",
        product.name, product.category, product.price,
        product.stock, product.minStockAlert, product.id
    )
    conn.commit()
    return product


def delete(product_id: str) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Products WHERE id=?", product_id)
    conn.commit()
