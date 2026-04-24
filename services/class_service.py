from typing import List
from database.db_connection import get_connection
from models.models import ClassSession


def get_all() -> List[ClassSession]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Classes")
    classes_rows = cur.fetchall()

    cur.execute("SELECT * FROM ClassEnrollments")
    enrollments = cur.fetchall()

    classes = []
    for row in classes_rows:
        enrolled = [str(e.memberId) for e in enrollments if str(e.classId) == str(row.id)]
        classes.append(ClassSession(
            id=str(row.id),
            name=row.name,
            trainerId=str(row.trainerId),
            time=row.time or "",
            dayOfWeek=row.dayOfWeek or "",
            capacity=int(row.capacity),
            enrolledMemberIds=enrolled
        ))
    return classes


def add(cls: ClassSession) -> ClassSession:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO Classes (id, name, trainerId, time, dayOfWeek, capacity) "
        "VALUES (?,?,?,?,?,?)",
        cls.id, cls.name, cls.trainerId, cls.time, cls.dayOfWeek, cls.capacity
    )
    conn.commit()
    return cls


def update(cls: ClassSession) -> ClassSession:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE Classes SET name=?, trainerId=?, time=?, dayOfWeek=?, capacity=? WHERE id=?",
        cls.name, cls.trainerId, cls.time, cls.dayOfWeek, cls.capacity, cls.id
    )
    # Sync enrollments
    cur.execute("DELETE FROM ClassEnrollments WHERE classId=?", cls.id)
    for mid in cls.enrolledMemberIds:
        cur.execute(
            "INSERT INTO ClassEnrollments (classId, memberId) VALUES (?,?)", cls.id, mid
        )
    conn.commit()
    return cls


def delete(class_id: str) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM ClassEnrollments WHERE classId=?", class_id)
    cur.execute("DELETE FROM Classes WHERE id=?", class_id)
    conn.commit()
