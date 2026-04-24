from typing import List, Optional
from database.db_connection import get_connection
from models.models import Event, EventParticipant


def get_all_events() -> List[Event]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Events ORDER BY date DESC, time DESC")
    records = []
    for row in cur.fetchall():
        records.append(Event(
            id=str(row.id),
            name=row.name,
            description=row.description or "",
            date=str(row.date) if row.date else "",
            time=row.time or "",
            location=row.location or "",
            capacity=row.capacity or 0,
            status=row.status or "UPCOMING"
        ))
    return records


def add_event(event: Event) -> Event:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO Events (id, name, description, date, time, location, capacity, status) "
        "VALUES (?,?,?,?,?,?,?,?)",
        event.id, event.name, event.description, event.date, event.time,
        event.location, event.capacity, event.status
    )
    conn.commit()
    return event


def update_event(event: Event) -> Event:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE Events SET name=?, description=?, date=?, time=?, location=?, capacity=?, status=? WHERE id=?",
        event.name, event.description, event.date, event.time,
        event.location, event.capacity, event.status, event.id
    )
    conn.commit()
    return event


def delete_event(event_id: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM EventParticipants WHERE eventId=?", event_id)
        cur.execute("DELETE FROM Events WHERE id=?", event_id)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Delete event error: {e}")
        return False


def get_participants_for_event(event_id: str) -> List[EventParticipant]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM EventParticipants WHERE eventId=? ORDER BY registerDate DESC", event_id)
    records = []
    for row in cur.fetchall():
        records.append(EventParticipant(
            id=str(row.id),
            eventId=str(row.eventId),
            memberId=str(row.memberId),
            memberName=row.memberName or "",
            registerDate=str(row.registerDate) if row.registerDate else "",
            status=row.status or "PENDING"
        ))
    return records


def add_participant(participant: EventParticipant) -> EventParticipant:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO EventParticipants (id, eventId, memberId, memberName, registerDate, status) "
        "VALUES (?,?,?,?,?,?)",
        participant.id, participant.eventId, participant.memberId,
        participant.memberName, participant.registerDate, participant.status
    )
    conn.commit()
    return participant


def update_participant_status(participant_id: str, status: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE EventParticipants SET status=? WHERE id=?", status, participant_id)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False
