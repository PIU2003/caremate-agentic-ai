import sqlite3

DATABASE_NAME = "caremate.db"


def get_connection():
    return sqlite3.connect(DATABASE_NAME)

def create_tables():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversations (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user TEXT,

        assistant TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reminders (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        request TEXT,

        result TEXT
    )
    """)

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

def save_conversation(user, assistant):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO conversations(user, assistant)
        VALUES(?, ?)
        """,
        (user, assistant)
    )

    conn.commit()
    conn.close()

def save_reminder(request, result):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO reminders(request, result)
        VALUES(?, ?)
        """,
        (request, result)
    )

    conn.commit()
    conn.close()

def save_health_note(question, advice):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO health_notes(question, advice)
        VALUES(?, ?)
        """,
        (question, advice)
    )

    conn.commit()
    conn.close()

def save_summary(input_text, summary):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO summaries(input, summary)
        VALUES(?, ?)
        """,
        (input_text, summary)
    )

    conn.commit()
    conn.close()

def get_reminders():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT request, result
        FROM reminders
        ORDER BY id DESC
    """)

    reminders = cursor.fetchall()

    conn.close()

    return reminders

def get_health_notes():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT question, advice
        FROM health_notes
        ORDER BY id DESC
    """)

    notes = cursor.fetchall()

    conn.close()

    return notes

def get_conversations():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user, assistant
        FROM conversations
        ORDER BY id DESC
    """)

    conversations = cursor.fetchall()

    conn.close()

    return conversations

def get_summaries():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT input, summary
        FROM summaries
        ORDER BY id DESC
    """)

    summaries = cursor.fetchall()

    conn.close()

    return summaries