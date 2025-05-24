
"""
chat_history.py

Provides SQLite-backed session-based chat history management for multi-turn character conversations.
"""
import sqlite3
from datetime import datetime
from typing import List, Optional, Tuple, Dict
from contextlib import contextmanager

from constants import (
    ROLE_USER,
    ROLE_CHARACTER,
    DEFAULT_CHAT_DB_FILE,
    DEFAULT_CHAT_HISTORY_LIMIT,
    ERROR_EMPTY_CHARACTER_NAME,
    ERROR_INVALID_ROLE,
    ERROR_EMPTY_MESSAGE,
    ERROR_INVALID_LIMIT,
    ERROR_DB_INIT_FAILED,
    ERROR_SESSION_OPERATION_FAILED,
    ERROR_MESSAGE_ADD_FAILED,
    ERROR_HISTORY_FETCH_FAILED,
    ERROR_HISTORY_RESET_FAILED,
    ERROR_SESSION_DELETE_FAILED,
    ERROR_HISTORY_EXPORT_FAILED,
    ERROR_SESSION_LIST_FAILED
)


class ChatHistoryService:
    """Service class for managing SQLite-backed chat history for character conversations."""
    
    DB_FILE: str = DEFAULT_CHAT_DB_FILE
    ROLE_USER: str = ROLE_USER
    ROLE_CHARACTER: str = ROLE_CHARACTER
    
    def __init__(self, db_file: Optional[str] = None):
        """Initialize the ChatHistoryService.
        
        Args:
            db_file: Optional database file path. Defaults to class constant DB_FILE.
        """
        self.db_file = db_file or self.DB_FILE
    
    @contextmanager
    def get_connection(self):
        """Get a SQLite DB connection with proper context management.
        
        Yields:
            sqlite3.Connection: Database connection object.
            
        Raises:
            sqlite3.Error: If database connection fails.
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            yield conn
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    def initialize_db(self) -> None:
        """Create tables if they do not exist.
        
        Raises:
            sqlite3.Error: If database initialization fails.
        """
        try:
            with self.get_connection() as conn:
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
        except sqlite3.Error as e:
            raise sqlite3.Error(f"{ERROR_DB_INIT_FAILED}: {e}")
    
    def get_or_create_session(self, character: str) -> int:
        """Get the chat session ID for a character; create session if not exists.
        
        Args:
            character: The character name to get or create a session for.
            
        Returns:
            int: The session ID.
            
        Raises:
            sqlite3.Error: If database operation fails.
            ValueError: If character name is empty or None.
        """
        if not character or not character.strip():
            raise ValueError(ERROR_EMPTY_CHARACTER_NAME)
            
        try:
            with self.get_connection() as conn:
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
                    return session_id
                # Create new session
                cur.execute(
                    "INSERT INTO chat_sessions (character, last_active) VALUES (?, ?)",
                    (character, datetime.utcnow()),
                )
                session_id = cur.lastrowid
                conn.commit()
                return session_id
        except sqlite3.Error as e:
            raise sqlite3.Error(f"{ERROR_SESSION_OPERATION_FAILED} '{character}': {e}")
    
    def add_message(self, session_id: int, role: str, message: str) -> None:
        """Append a message to session history.
        
        Args:
            session_id: The session ID to add the message to.
            role: The role of the message sender ('user' or 'character').
            message: The message content.
            
        Raises:
            sqlite3.Error: If database operation fails.
            ValueError: If role is not valid or message is empty.
        """
        if role not in [self.ROLE_USER, self.ROLE_CHARACTER]:
            raise ValueError(f"{ERROR_INVALID_ROLE} '{self.ROLE_USER}' or '{self.ROLE_CHARACTER}'")
        if not message or not message.strip():
            raise ValueError(ERROR_EMPTY_MESSAGE)
            
        try:
            ts = datetime.utcnow()
            with self.get_connection() as conn:
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
        except sqlite3.Error as e:
            raise sqlite3.Error(f"{ERROR_MESSAGE_ADD_FAILED} {session_id}: {e}")
    
    def get_history(self, session_id: int, limit: int = DEFAULT_CHAT_HISTORY_LIMIT) -> List[Tuple[str, str]]:
        """Get session message history (role, message), most recent last.
        
        Args:
            session_id: The session ID to get history for.
            limit: Maximum number of messages to return. Can truncate older turns.
            
        Returns:
            List[Tuple[str, str]]: List of (role, message) tuples.
            
        Raises:
            sqlite3.Error: If database operation fails.
            ValueError: If limit is not positive.
        """
        if limit <= 0:
            raise ValueError(ERROR_INVALID_LIMIT)
            
        try:
            with self.get_connection() as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT role, message FROM chat_messages WHERE session_id=? ORDER BY id ASC LIMIT ?",
                    (session_id, limit),
                )
                messages = cur.fetchall()
                return messages
        except sqlite3.Error as e:
            raise sqlite3.Error(f"{ERROR_HISTORY_FETCH_FAILED} {session_id}: {e}")
    
    def reset_history(self, session_id: int) -> None:
        """Delete all messages in a session but leave the session intact.
        
        Args:
            session_id: The session ID to reset.
            
        Raises:
            sqlite3.Error: If database operation fails.
        """
        try:
            with self.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM chat_messages WHERE session_id=?", (session_id,))
                conn.commit()
        except sqlite3.Error as e:
            raise sqlite3.Error(f"{ERROR_HISTORY_RESET_FAILED} {session_id}: {e}")
    
    def delete_session(self, session_id: int) -> None:
        """Delete the entire chat session (and its messages).
        
        Args:
            session_id: The session ID to delete.
            
        Raises:
            sqlite3.Error: If database operation fails.
        """
        try:
            with self.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM chat_sessions WHERE id=?", (session_id,))
                conn.commit()
        except sqlite3.Error as e:
            raise sqlite3.Error(f"{ERROR_SESSION_DELETE_FAILED} {session_id}: {e}")
    
    def export_history(self, session_id: int) -> List[Dict[str, str]]:
        """Export session message history as a list of dicts.
        
        Args:
            session_id: The session ID to export history for.
            
        Returns:
            List[Dict[str, str]]: List of dictionaries with keys 'role', 'message', 'timestamp'.
            
        Raises:
            sqlite3.Error: If database operation fails.
        """
        try:
            with self.get_connection() as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT role, message, timestamp FROM chat_messages WHERE session_id=? ORDER BY id ASC",
                    (session_id,),
                )
                rows = cur.fetchall()
                return [
                    {"role": role, "message": msg, "timestamp": ts}
                    for role, msg, ts in rows
                ]
        except sqlite3.Error as e:
            raise sqlite3.Error(f"{ERROR_HISTORY_EXPORT_FAILED} {session_id}: {e}")
    
    def list_sessions(self, character: Optional[str] = None) -> List[Tuple[int, str, str]]:
        """List all chat sessions, optionally filtered by character.
        
        Args:
            character: Optional character name to filter sessions by.
            
        Returns:
            List[Tuple[int, str, str]]: List of (id, character, last_active) tuples.
            
        Raises:
            sqlite3.Error: If database operation fails.
        """
        try:
            with self.get_connection() as conn:
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
                return sessions
        except sqlite3.Error as e:
            raise sqlite3.Error(f"{ERROR_SESSION_LIST_FAILED}: {e}")


# Global service instance for backward compatibility
_chat_history_service = ChatHistoryService()

# Backward compatibility functions
def get_connection():
    """Get a SQLite DB connection."""
    return _chat_history_service.get_connection()

def initialize_db():
    """Create tables if they do not exist."""
    return _chat_history_service.initialize_db()

def get_or_create_session(character: str) -> int:
    """
    Get the chat session ID for a character; create session if not exists.
    Returns session_id.
    """
    return _chat_history_service.get_or_create_session(character)

def add_message(session_id: int, role: str, message: str):
    """Append a message to session history."""
    return _chat_history_service.add_message(session_id, role, message)

def get_history(session_id: int, limit: int = DEFAULT_CHAT_HISTORY_LIMIT) -> List[Tuple[str, str]]:
    """Get session message history (role, message), most recent last. Limit can truncate older turns."""
    return _chat_history_service.get_history(session_id, limit)

def reset_history(session_id: int):
    """Delete all messages in a session but leave the session intact."""
    return _chat_history_service.reset_history(session_id)

def delete_session(session_id: int):
    """Delete the entire chat session (and its messages)."""
    return _chat_history_service.delete_session(session_id)

def export_history(session_id: int) -> List[Dict]:
    """Export session message history as a list of dicts (role, message, timestamp)."""
    return _chat_history_service.export_history(session_id)

def list_sessions(character: Optional[str] = None) -> List[Tuple[int, str, str]]:
    """List all chat sessions, optionally filtered by character. Returns (id, character, last_active)."""
    return _chat_history_service.list_sessions(character)

# Ensure tables exist if script is run
if __name__ == "__main__":
    try:
        initialize_db()
        print("Chat history DB initialized.")
    except Exception as e:
        print(f"Failed to initialize chat history DB: {e}")
