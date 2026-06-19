# https://www.geeksforgeeks.org/sql/sql-cheat-sheet/
# copilot helped me clean up the queries
import sqlite3
import time

DB_PATH = "chat.db"


def db_execute(query, params=(), fetchone=False, fetchall=False, commit=False):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)

            if commit:
                conn.commit()

            if fetchone:
                return cursor.fetchone()

            if fetchall:
                return cursor.fetchall()

            return cursor.rowcount or cursor.lastrowid

    except Exception as e:
        print(f"DB ERROR: {e}")
        return None


def db_send_message(message, user_origin, user_destination):
    return db_execute(
        """
        INSERT INTO messages (message, user_origin, user_destination, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (message, user_origin, user_destination, int(time.time()), int(time.time())),
        commit=True,
    )


def db_delete_message(message_id):
    return db_execute(
        """
        UPDATE messages SET is_deleted = 1, updated_at = ? WHERE id = ?
        """,
        (int(time.time()), message_id),
        commit=True,
    )


def db_edit_message(message_id, message):
    return db_execute(
        """
        UPDATE messages SET message = ?, updated_at = ? WHERE id = ?
        """,
        (message, int(time.time()), message_id),
        commit=True,
    )


def db_get_changed_or_new_messages(user_origin, user_destination, last_seen_time):
    rows = db_execute(
        """
        SELECT id, message, user_origin, user_destination, created_at, updated_at
        FROM messages
        WHERE (
            (user_origin = ? AND user_destination = ?)
            OR
            (user_origin = ? AND user_destination = ?)
        )
        AND updated_at > ?
        AND is_deleted = 0
        ORDER BY updated_at ASC
        """,
        (user_origin, user_destination, user_destination, user_origin, last_seen_time),
        fetchall=True,
    )

    return (
        [
            {
                "id": r[0],
                "message": r[1],
                "user_origin": r[2],
                "user_destination": r[3],
                "created_at": r[4],
                "updated_at": r[5],
            }
            for r in rows  # type: ignore
        ]
        if rows
        else []
    )


def db_check_owner_of_message_id(message_id):
    user_id = db_execute(
        """
        SELECT user_origin FROM messages WHERE id = ?
        """,
        (message_id,),
        fetchone=True,
    )
    return user_id[0] if user_id else None  # type: ignore


def db_initial_load(user_origin, user_destination, limit):
    rows = db_execute(
        """
        SELECT id, message, user_origin, user_destination, created_at, updated_at
        FROM messages
        WHERE (
            (user_origin = ? AND user_destination = ?)
            OR
            (user_origin = ? AND user_destination = ?)
        )
        AND is_deleted = 0
        ORDER BY id DESC
        LIMIT ?
        """,
        (user_origin, user_destination, user_destination, user_origin, limit),
        fetchall=True,
    )

    return (
        [
            {
                "id": r[0],
                "message": r[1],
                "user_origin": r[2],
                "user_destination": r[3],
                "created_at": r[4],
                "updated_at": r[5],
            }
            for r in rows  # type: ignore
        ]
        if rows
        else []
    )


def db_load_more(user_origin, user_destination, limit, before_id):
    rows = db_execute(
        """
        SELECT id, message, user_origin, user_destination, created_at, updated_at
        FROM messages
        WHERE (
            (user_origin = ? AND user_destination = ?)
            OR
            (user_origin = ? AND user_destination = ?)
        )
        AND id < ?
        AND is_deleted = 0
        ORDER BY id DESC
        LIMIT ?
        """,
        (
            user_origin,
            user_destination,
            user_destination,
            user_origin,
            before_id,
            limit,
        ),
        fetchall=True,
    )

    return (
        [
            {
                "id": r[0],
                "message": r[1],
                "user_origin": r[2],
                "user_destination": r[3],
                "created_at": r[4],
                "updated_at": r[5],
            }
            for r in rows  # type: ignore
        ]
        if rows
        else []
    )


def db_check_username_and_password(username, password):
    row = db_execute(
        "SELECT id FROM users WHERE username = ? AND password = ?",
        (username, password),
        fetchone=True,
    )
    return row[0] if row else None  # type: ignore


def db_register_user(username, password):
    return db_execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (username, password),
        commit=True,
    )


def db_username_exists(username):
    row = db_execute(
        "SELECT id FROM users WHERE username = ?", (username,), fetchone=True
    )
    return row is not None


def db_get_users(user_origin):
    rows = db_execute(
        "SELECT id, username FROM users WHERE id != ?", (user_origin,), fetchall=True
    )

    return [{"id": r[0], "username": r[1]} for r in rows] if rows else []  # type: ignore
