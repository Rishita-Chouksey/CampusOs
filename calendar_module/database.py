import sqlite3

DATABASE = "events.db"


# Connect to database
def connect():
    return sqlite3.connect(DATABASE)


# Create Events Table
def create_table():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        subject TEXT,
        event_date TEXT,
        event_time TEXT,
        event_type TEXT,
        reminder TEXT
    )
    """)

    conn.commit()
    conn.close()


# Add Event
def add_event(title, subject, date, time, event_type, reminder):

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO events
    (title, subject, event_date, event_time, event_type, reminder)

    VALUES (?, ?, ?, ?, ?, ?)

    """, (
        title,
        subject,
        date,
        time,
        event_type,
        reminder
    ))

    conn.commit()
    conn.close()


# Get All Events
def get_events():

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM events
    ORDER BY event_date
    """)

    data = cursor.fetchall()

    conn.close()

    return data


# Delete Event
def delete_event(event_id):

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM events
    WHERE id=?
    """, (event_id,))

    conn.commit()
    conn.close()


# Update Event
def update_event(
        event_id,
        title,
        subject,
        date,
        time,
        event_type,
        reminder):

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE events

    SET

    title=?,
    subject=?,
    event_date=?,
    event_time=?,
    event_type=?,
    reminder=?

    WHERE id=?

    """, (

        title,
        subject,
        date,
        time,
        event_type,
        reminder,
        event_id

    ))

    conn.commit()
    conn.close()


# Search Events by Date
def get_events_by_date(date):

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM events

    WHERE event_date=?

    """, (date,))

    data = cursor.fetchall()

    conn.close()

    return data


# Search Upcoming Events
def get_upcoming_events():

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *

    FROM events

    ORDER BY event_date

    LIMIT 10
    """)

    data = cursor.fetchall()

    conn.close()

    return data


# Initialize Database
create_table()