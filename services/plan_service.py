from typing import List
from database.db_connection import get_connection
from models.models import Plan


def get_all() -> List[Plan]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Plans")
    plans = []
    for row in cur.fetchall():
        plans.append(Plan(
            id=str(row.id),
            name=row.name,
            type=row.type,
            price=float(row.price),
            description=row.description or "",
            durationMonths=row.durationMonths,
            sessions=row.sessions,
        ))
    return plans


def add(plan: Plan) -> Plan:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO Plans (id, name, type, price, description, durationMonths, sessions) "
        "VALUES (?,?,?,?,?,?,?)",
        plan.id, plan.name, plan.type, plan.price,
        plan.description, plan.durationMonths, plan.sessions
    )
    conn.commit()
    return plan


def update(plan: Plan) -> Plan:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE Plans SET name=?, type=?, price=?, description=?, durationMonths=?, sessions=? "
        "WHERE id=?",
        plan.name, plan.type, plan.price, plan.description,
        plan.durationMonths, plan.sessions, plan.id
    )
    conn.commit()
    return plan


def delete(plan_id: str) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Plans WHERE id=?", plan_id)
    conn.commit()
