import random
import time
from core.constants import FILES
from core.file_handler import read_table, write_table


OPEN = "OPEN"
DONE = "DONE"
UNREAD = "UNREAD"
READ = "READ"
ADMIN = "ADMIN"


def legacy_session_id(username):
    return f"legacy-{username}"


def parse_message(row):
    if len(row) >= 6:
        return {
            "id": row[0],
            "session_id": row[1],
            "sender": row[2],
            "receiver": row[3],
            "text": row[4],
            "read_status": row[5],
            "row": row,
        }
    if len(row) >= 4:
        sender, receiver = row[1], row[2]
        username = receiver if sender == ADMIN else sender
        return {
            "id": row[0],
            "session_id": legacy_session_id(username),
            "sender": sender,
            "receiver": receiver,
            "text": row[3],
            "read_status": row[4] if len(row) >= 5 else READ,
            "row": row,
        }
    return None


def get_sessions(username):
    sessions = []
    seen = set()
    for row in read_table(FILES["message_sessions"]):
        if len(row) >= 4 and row[1] == username:
            sessions.append(row)
            seen.add(row[0])

    has_legacy = False
    for row in read_table(FILES["messages"]):
        msg = parse_message(row)
        if not msg:
            continue
        if msg["session_id"] == legacy_session_id(username):
            has_legacy = True
            break

    if has_legacy and legacy_session_id(username) not in seen:
        sessions.insert(0, [legacy_session_id(username), username, "Current", get_conversation_status(username)])

    return sessions


def ticket_session_title(username, ticket_no):
    return f"{username}-ticket{ticket_no}"


def create_session(username, title=None):
    rows = read_table(FILES["message_sessions"])
    ticket_no = sum(1 for row in rows if len(row) >= 2 and row[1] == username) + 1
    title = title or ticket_session_title(username, ticket_no)
    session_id = f"{username}-{int(time.time() * 1000)}-{random.randint(10000, 99999)}"
    rows.append([session_id, username, title, OPEN])
    write_table(FILES["message_sessions"], rows)
    return session_id


def get_session_status(session_id, username):
    for row in get_sessions(username):
        if row[0] == session_id:
            return row[3]
    return OPEN


def set_session_status(session_id, username, status):
    if session_id == legacy_session_id(username):
        set_conversation_status(username, status)
        return

    rows = read_table(FILES["message_sessions"])
    for row in rows:
        if len(row) >= 4 and row[0] == session_id:
            row[3] = status
            break
    write_table(FILES["message_sessions"], rows)


def get_session_messages(session_id, username):
    messages = []
    for row in read_table(FILES["messages"]):
        msg = parse_message(row)
        if not msg:
            continue
        if msg["session_id"] != session_id:
            continue
        is_from_user = msg["sender"] == username and msg["receiver"] == ADMIN
        is_to_user = msg["sender"] == ADMIN and msg["receiver"] == username
        if is_from_user or is_to_user:
            messages.append(msg)
    return messages


def get_conversation_status(username):
    for row in read_table(FILES["message_status"]):
        if len(row) >= 2 and row[0] == username:
            return row[1]
    return OPEN


def set_conversation_status(username, status):
    rows = read_table(FILES["message_status"])
    updated = False
    for row in rows:
        if len(row) >= 2 and row[0] == username:
            row[1] = status
            updated = True
            break
    if not updated:
        rows.append([username, status])
    write_table(FILES["message_status"], rows)


def count_unread(receiver):
    total = 0
    for row in read_table(FILES["messages"]):
        msg = parse_message(row)
        if msg and msg["receiver"] == receiver and msg["read_status"] == UNREAD:
            total += 1
    return total


def mark_conversation_read(viewer, other_party, session_id=None):
    rows = read_table(FILES["messages"])
    changed = False
    for row in rows:
        msg = parse_message(row)
        if not msg:
            continue
        if session_id and msg["session_id"] != session_id:
            continue
        is_between_parties = (
            (msg["sender"] == viewer and msg["receiver"] == other_party) or
            (msg["sender"] == other_party and msg["receiver"] == viewer)
        )
        if msg["read_status"] == UNREAD and msg["receiver"] == viewer and is_between_parties:
            if len(row) >= 6:
                row[5] = READ
            elif len(row) >= 5:
                row[4] = READ
            changed = True
    if changed:
        write_table(FILES["messages"], rows)


def mark_all_read(receiver):
    rows = read_table(FILES["messages"])
    changed = False
    for row in rows:
        msg = parse_message(row)
        if not msg:
            continue
        if msg["receiver"] == receiver and msg["read_status"] == UNREAD:
            if len(row) >= 6:
                row[5] = READ
            elif len(row) >= 5:
                row[4] = READ
            changed = True
    if changed:
        write_table(FILES["messages"], rows)
