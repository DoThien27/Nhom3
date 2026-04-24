from typing import List
from database.db_connection import get_connection
from models.models import Member


def get_all() -> List[Member]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT m.*, p.name as activePlanName, u.fullName as assignedPTName
        FROM Members m
        LEFT JOIN Plans p ON m.activePlanId = p.id
        LEFT JOIN Users u ON m.assignedPTId = u.id
    """)
    members = []
    for row in cur.fetchall():
        members.append(Member(
            id=str(row.id),
            fullName=row.fullName,
            phone=row.phone or "",
            email=row.email or "",
            joinDate=str(row.joinDate) if row.joinDate else "",
            status=row.status or "ACTIVE",
            activePlanId=row.activePlanId,
            activePlanName=row.activePlanName,
            expiryDate=str(row.expiryDate) if row.expiryDate else None,
            assignedPTId=row.assignedPTId,
            assignedPTName=row.assignedPTName,
            weight=float(row.weight) if row.weight else 0.0,
            previousWeight=float(row.previousWeight) if row.previousWeight else 0.0,
            avatar=row.avatar,
            username=row.username,
            password=row.password,
            homeTown=row.homeTown if hasattr(row, 'homeTown') else None,
        ))
    return members


def add(member: Member) -> Member:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO Members (id, fullName, phone, email, joinDate, status, weight, "
        "avatar, username, password) VALUES (?,?,?,?,?,?,?,?,?,?)",
        member.id, member.fullName, member.phone, member.email,
        member.joinDate, member.status, member.weight,
        member.avatar, member.username, member.password
    )
    conn.commit()
    return member


def update(member: Member) -> Member:
    conn = get_connection()
    cur = conn.cursor()
    # Lấy cân nặng cũ
    cur.execute("SELECT weight FROM Members WHERE id=?", member.id)
    row = cur.fetchone()
    prev_weight = member.previousWeight
    if row and row.weight != member.weight:
        prev_weight = float(row.weight) if row.weight else 0.0

    cur.execute("""
        UPDATE Members SET
            fullName=?, phone=?, email=?, status=?,
            weight=?, previousWeight=?,
            activePlanId=?, expiryDate=?, assignedPTId=?,
            username=?
        WHERE id=?
    """,
        member.fullName, member.phone, member.email, member.status,
        member.weight, prev_weight,
        member.activePlanId, member.expiryDate, member.assignedPTId,
        member.username, member.id
    )
    if member.password:
        cur.execute("UPDATE Members SET password=? WHERE id=?", member.password, member.id)
    conn.commit()
    member.previousWeight = prev_weight
    return member


def delete(member_id: str) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Members WHERE id=?", member_id)
    conn.commit()
