import sqlite3
from datetime import datetime, timedelta

DATABASE_NAME = "caremate.db"


def get_connection():
    return sqlite3.connect(DATABASE_NAME)


def _ensure_reminder_columns(cursor):
    cursor.execute("PRAGMA table_info(reminders)")
    columns = {row[1] for row in cursor.fetchall()}
    for name, definition in [
        ("title", "TEXT"),
        ("remind_at", "TEXT"),
        ("recurrence", "TEXT DEFAULT 'none'"),
        ("status", "TEXT DEFAULT 'pending'"),
        ("created_at", "TEXT DEFAULT CURRENT_TIMESTAMP"),
    ]:
        if name not in columns:
            cursor.execute(
                f"ALTER TABLE reminders ADD COLUMN {name} {definition}"
            )


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL DEFAULT 'New conversation',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            agent TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request TEXT,
            result TEXT,
            title TEXT,
            remind_at TEXT,
            recurrence TEXT DEFAULT 'none',
            status TEXT DEFAULT 'pending',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    _ensure_reminder_columns(cursor)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS health_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            advice TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            input TEXT,
            summary TEXT
        )
    """)

    conn.commit()
    conn.close()


def create_chat_session():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_sessions DEFAULT VALUES")
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id


def get_chat_sessions():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title FROM chat_sessions ORDER BY id DESC"
    )
    sessions = cursor.fetchall()
    conn.close()
    return sessions


def save_chat_message(session_id, role, content, agent=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO chat_messages(session_id, role, content, agent)
        VALUES(?, ?, ?, ?)
        """,
        (session_id, role, content, agent),
    )
    if role == "user":
        cursor.execute(
            """
            UPDATE chat_sessions
            SET title = ?
            WHERE id = ? AND title = 'New conversation'
            """,
            (content[:30], session_id),
        )
    conn.commit()
    conn.close()


def get_chat_messages(session_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT role, content, agent
        FROM chat_messages
        WHERE session_id = ?
        ORDER BY id ASC
        """,
        (session_id,),
    )
    messages = cursor.fetchall()
    conn.close()
    return messages


def delete_chat_session(session_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM chat_messages WHERE session_id = ?", (session_id,)
    )
    cursor.execute(
        "DELETE FROM chat_sessions WHERE id = ?", (session_id,)
    )
    conn.commit()
    conn.close()


def save_reminder(
    request,
    result,
    title=None,
    remind_at=None,
    recurrence="none",
    status="pending",
):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO reminders(
            request, result, title, remind_at, recurrence, status
        )
        VALUES(?, ?, ?, ?, ?, ?)
        """,
        (
            request,
            result,
            title or request[:50],
            remind_at,
            recurrence or "none",
            status,
        ),
    )
    reminder_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return reminder_id


def get_due_reminders(now=None):
    now = now or datetime.now()
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, title, request, result, remind_at, recurrence, status
        FROM reminders
        WHERE status = 'pending'
          AND remind_at IS NOT NULL
          AND remind_at <= ?
        ORDER BY remind_at ASC
        """,
        (now_str,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": row[0],
            "title": row[1] or "Reminder",
            "request": row[2],
            "result": row[3],
            "remind_at": row[4],
            "recurrence": row[5] or "none",
            "status": row[6],
        }
        for row in rows
    ]


def complete_or_reschedule_reminder(reminder_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT remind_at, recurrence FROM reminders WHERE id = ?",
        (reminder_id,),
    )
    row = cursor.fetchone()
    if not row:
        conn.close()
        return

    remind_at, recurrence = row
    recurrence = (recurrence or "none").lower()

    if recurrence == "daily" and remind_at:
        try:
            current = datetime.strptime(remind_at, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            current = datetime.now()
        next_time = current + timedelta(days=1)
        while next_time <= datetime.now():
            next_time += timedelta(days=1)
        cursor.execute(
            """
            UPDATE reminders
            SET remind_at = ?, status = 'pending'
            WHERE id = ?
            """,
            (next_time.strftime("%Y-%m-%d %H:%M:%S"), reminder_id),
        )
    else:
        cursor.execute(
            "UPDATE reminders SET status = 'completed' WHERE id = ?",
            (reminder_id,),
        )

    conn.commit()
    conn.close()


def save_health_note(question, advice):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO health_notes(question, advice) VALUES(?, ?)",
        (question, advice),
    )
    conn.commit()
    conn.close()


def save_summary(input_text, summary):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO summaries(input, summary) VALUES(?, ?)",
        (input_text, summary),
    )
    conn.commit()
    conn.close()


def get_reminders(include_completed=False):
    conn = get_connection()
    cursor = conn.cursor()
    if include_completed:
        cursor.execute(
            """
            SELECT id, title, request, result, remind_at, recurrence, status
            FROM reminders
            ORDER BY id DESC
            """
        )
    else:
        cursor.execute(
            """
            SELECT id, title, request, result, remind_at, recurrence, status
            FROM reminders
            WHERE status != 'completed'
            ORDER BY
                CASE WHEN remind_at IS NULL THEN 1 ELSE 0 END,
                remind_at ASC
            """
        )
    reminders = cursor.fetchall()
    conn.close()
    return reminders


def delete_reminder(reminder_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
    conn.commit()
    conn.close()


def get_health_notes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT question, advice FROM health_notes ORDER BY id DESC"
    )
    notes = cursor.fetchall()
    conn.close()
    return notes
