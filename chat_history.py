"""
chat_history.py

Provides SQLite-backed session-based chat history management for multi-turn character conversations.
"""
import sqlite3
from datetime import datetime
from typing import List, Optional, Tuple, Dict

DB_FILE = "lore_chat_history.db"

def get_connection():
    """Get a SQLite DB connection."""
    return sqlite3.connect(DB_FILE)

def initialize_db():
    """Create tables if they do not exist."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS chat_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        character TEXT NOT NULL,
        last_active TIMESTAMP NOT NULL
    )''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        role TEXT CHECK( role IN ('user','character') ) NOT NULL,
        message TEXT NOT NULL,
        timestamp TIMESTAMP NOT NULL,
        FOREIGN KEY(session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
    )''')
    conn.commit()
    conn.close()

def get_or_create_session(character: str) -> int:
    """
    Get the chat session ID for a character; create session if not exists.
    Returns session_id.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id FROM chat_sessions WHERE character=? ORDER BY last_active DESC LIMIT 1",
        (character,)
    )
    row = cur.fetchone()
    if row:
        session_id = row[0]
        cur.execute(
            "UPDATE chat_sessions SET last_active=? WHERE id=?",
            (datetime.utcnow(), session_id),
        )
        conn.commit()
        conn.close()
        return session_id
    # Create new session
    cur.execute(
        "INSERT INTO chat_sessions (character, last_active) VALUES (?, ?)",
        (character, datetime.utcnow()),
    )
    session_id = cur.lastrowid
    conn.commit()
    conn.close()
    return session_id

def add_message(session_id: int, role: str, message: str):
    """Append a message to session history."""
    ts = datetime.utcnow()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO chat_messages (session_id, role, message, timestamp) VALUES (?, ?, ?, ?)",
        (session_id, role, message, ts),
    )
    cur.execute(
        "UPDATE chat_sessions SET last_active=? WHERE id=?",
        (ts, session_id),
    )
    conn.commit()
    conn.close()

def get_history(session_id: int, limit: int = 20) -> List[Tuple[str, str]]:
    """Get session message history (role, message), most recent last. Limit can truncate older turns."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT role, message FROM chat_messages WHERE session_id=? ORDER BY id ASC LIMIT ?",
        (session_id, limit),
    )
    messages = cur.fetchall()
    conn.close()
    return messages

def reset_history(session_id: int):
    """Delete all messages in a session but leave the session intact."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM chat_messages WHERE session_id=?", (session_id,))
    conn.commit()
    conn.close()

def delete_session(session_id: int):
    """Delete the entire chat session (and its messages)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM chat_sessions WHERE id=?", (session_id,))
    conn.commit()
    conn.close()

def export_history(session_id: int) -> List[Dict]:
    """Export session message history as a list of dicts (role, message, timestamp)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT role, message, timestamp FROM chat_messages WHERE session_id=? ORDER BY id ASC",
        (session_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return [
        {"role": role, "message": msg, "timestamp": ts}
        for role, msg, ts in rows
    ]

def list_sessions(character: Optional[str] = None) -> List[Tuple[int, str, str]]:
    """List all chat sessions, optionally filtered by character. Returns (id, character, last_active)."""
    conn = get_connection()
    cur = conn.cursor()
    if character:
        cur.execute(
            "SELECT id, character, last_active FROM chat_sessions WHERE character=? ORDER BY last_active DESC",
            (character,),
        )
    else:
        cur.execute(
            "SELECT id, character, last_active FROM chat_sessions ORDER BY last_active DESC"
        )
    sessions = cur.fetchall()
    conn.close()
    return sessions

# Ensure tables exist if script is run
if __name__ == "__main__":
    initialize_db()
    print("Chat history DB initialized.")
