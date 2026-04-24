from typing import Optional, List
from database.db_connection import get_connection
from models.models import User


def login(username: str, password: str) -> Optional[User]:
    conn = get_connection()
    cur = conn.cursor()
    # Kiểm tra bảng Users
    cur.execute(
        "SELECT id, username, fullName, role, specialty, activeStudents, avatar "
        "FROM Users WHERE username=? AND password=?",
        username, password
    )
    row = cur.fetchone()
    if row:
        return User(
            id=row.id, username=row.username, fullName=row.fullName,
            role=row.role, specialty=row.specialty,
            activeStudents=row.activeStudents or 0, avatar=row.avatar
        )
    # Kiểm tra bảng Members
    cur.execute(
        "SELECT id, username, fullName, status "
        "FROM Members WHERE username=? AND password=?",
        username, password
    )
    row = cur.fetchone()
    if row:
        return User(
            id=row.id, username=row.username,
            fullName=row.fullName, role="MEMBER"
        )
    return None


def get_all() -> List[User]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, username, fullName, role, specialty, activeStudents, avatar FROM Users"
    )
    users = []
    for row in cur.fetchall():
        users.append(User(
            id=row.id, username=row.username, fullName=row.fullName,
            role=row.role, specialty=row.specialty,
            activeStudents=row.activeStudents or 0, avatar=row.avatar
        ))
    return users


def add(user: User) -> User:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO Users (id, username, password, fullName, role, specialty, activeStudents, avatar) "
        "VALUES (?,?,?,?,?,?,?,?)",
        user.id, user.username, user.password, user.fullName,
        user.role, user.specialty, user.activeStudents or 0, user.avatar
    )
    conn.commit()
    return user


def update(user: User) -> User:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE Users SET username=?, fullName=?, role=?, specialty=?, activeStudents=?, avatar=? "
        "WHERE id=?",
        user.username, user.fullName, user.role, user.specialty,
        user.activeStudents or 0, user.avatar, user.id
    )
    if user.password:
        cur.execute("UPDATE Users SET password=? WHERE id=?", user.password, user.id)
    conn.commit()
    return user


def delete(user_id: str) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Users WHERE id=?", user_id)
    conn.commit()
