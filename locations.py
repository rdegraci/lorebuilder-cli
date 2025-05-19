"""
locations.py

Location/scene functions, world and character movement logic.
Exports: look, save_look, go, get_db_connection, and other navigation commands.
Required: Must call init_locations(config, chat_history) before use.
"""

import sqlite3
import uuid
from datetime import datetime
from rich import print as rprint
import json

# Globals initialized via init_locations
_config = None
_chat_history = None

def init_locations(config, chat_history):
    """
    Initialize the locations module with configuration and dependencies.
    This must be called before using any other functions in this module.
    
    Args:
        config (dict): Application configuration
        chat_history: Chat history module for character interactions
    """
    global _config, _chat_history
    _config = config
    _chat_history = chat_history
    # Initialize the locations database
    initialize_locations_db()

def get_db_connection():
    """ 
    Helper for consistent DB connections (used by app.py and locations functions).
    
    Returns:
        sqlite3.Connection: A connection to the locations database
    """
    db_path = _config.get("locations_db_path", "chat.db")
    return sqlite3.connect(db_path)

def initialize_locations_db():
    """
    Create necessary tables in the locations database if they don't exist.
    Called automatically during init_locations.
    """
    conn = get_db_connection()
    c = conn.cursor()
    
    # Create table for tracking character locations
    c.execute('''
    CREATE TABLE IF NOT EXISTS character_location (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        character_name TEXT NOT NULL,
        location_id TEXT NOT NULL,
        timestamp TEXT NOT NULL
    )
    ''')
    
    # Create table for location definitions (for permanent locations)
    c.execute('''
    CREATE TABLE IF NOT EXISTS locations (
        location_id TEXT PRIMARY KEY,
        display_name TEXT NOT NULL,
        description TEXT NOT NULL,
        exits TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    ''')
    
    conn.commit()
    conn.close()
    rprint("[dim]Locations database initialized.[/dim]")

def look(character_name):
    """
    Return scene/location info for current position of character_name.
    
    Args:
        character_name (str): Name of the character to get location for
        
    Returns:
        dict: Scene information including location_id, display_name, description, and exits
    """
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT location_id FROM character_location WHERE character_name = ? ORDER BY timestamp DESC LIMIT 1", 
              (character_name,))
    row = c.fetchone()
    
    if not row:
        # Character has no location yet
        conn.close()
        return {
            "location_id": "unknown",
            "display_name": "Nowhere",
            "description": "The character is not located anywhere.",
            "exits": [],
            "_explanation": "Character has no recorded location.",
        }
    
    location_id = row[0]
    
    # Check for defined location in the locations table
    c.execute("SELECT display_name, description, exits FROM locations WHERE location_id = ?", 
              (location_id,))
    location_row = c.fetchone()
    conn.close()
    
    if location_row:
        # Return stored location data
        display_name, description, exits_json = location_row
        return {
            "location_id": location_id,
            "display_name": display_name,
            "description": description,
            "exits": json.loads(exits_json),
            "_explanation": "Retrieved from locations database.",
        }
    else:
        # Return placeholder data for now
        scene_info = {
            "location_id": location_id,
            "display_name": f"Scene {location_id}",
            "description": f"This is a location with ID {location_id}.",
            "exits": ["north", "east", "down"],
            "_explanation": "Generated placeholder (location not in database).",
        }
        return scene_info

def save_look(args, context):
    """
    Command handler: Save/look at current location for a character.
    Usage: save_look <character_name>
    
    Args:
        args (list): Command arguments
        context (dict): Shared context dictionary
    """
    if not args:
        rprint("[yellow]Usage: save_look <character_name>")
        return
    
    char_name = args[0]
    scene = look(char_name)
    context['last_look_result'] = scene
    
    rprint(f"[green]Look saved for '{char_name}'. Location: {scene['display_name']}.")

def save_location(location_id, display_name, description, exits):
    """
    Store a location definition in the database.
    
    Args:
        location_id (str): Unique identifier for the location
        display_name (str): Human-readable name of the location
        description (str): Detailed description of the location
        exits (list): List of available exit directions
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute(
            "INSERT OR REPLACE INTO locations (location_id, display_name, description, exits, created_at) VALUES (?, ?, ?, ?, ?)",
            (location_id, display_name, description, json.dumps(exits), datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        rprint(f"[red]Error saving location: {e}")
        return False

def go(args, context):
    """
    Command handler: Move to another location.
    Usage: go <character_name> <direction>
    
    Args:
        args (list): Command arguments
        context (dict): Shared context dictionary
    """
    if len(args) < 2:
        rprint("[yellow]Usage: go <character_name> <direction>")
        return
    
    char_name, direction = args[0], args[1]
    
    # Get current location
    current_scene = look(char_name)
    
    # Check if direction is valid for current location
    if direction not in current_scene.get("exits", []):
        rprint(f"[red]Cannot go {direction} from here. Available exits: {', '.join(current_scene.get('exits', []))}.")
        return
    
    # Generate a new location ID
    new_loc = str(uuid.uuid4())[:8]
    
    # Update character's location
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO character_location (character_name, location_id, timestamp) VALUES (?, ?, datetime('now'))", 
        (char_name, new_loc)
    )
    conn.commit()
    conn.close()
    
    # Get the new scene info
    scene = look(char_name)
    context['last_look_result'] = scene
    
    rprint(f"[green]{char_name} moved {direction}. Now at {scene['display_name']} ({scene['location_id']}).")

def reset_location(args, context):
    """
    Command handler: Reset character's location.
    Usage: reset <character_name>
    
    Args:
        args (list): Command arguments
        context (dict): Shared context dictionary
    """
    if not args:
        rprint("[yellow]Usage: reset <character_name>")
        return
    
    char_name = args[0]
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM character_location WHERE character_name = ?", (char_name,))
    conn.commit()
    conn.close()
    
    rprint(f"[magenta]{char_name}'s location has been reset.")

def history(args, context):
    """
    Command handler: Show location history for character.
    Usage: history <character_name>
    
    Args:
        args (list): Command arguments
        context (dict): Shared context dictionary
    """
    if not args:
        rprint("[yellow]Usage: history <character_name>")
        return
    
    char_name = args[0]
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "SELECT location_id, timestamp FROM character_location WHERE character_name = ? ORDER BY timestamp DESC LIMIT 10", 
        (char_name,)
    )
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        rprint(f"[dim]No location history for '{char_name}'.")
        return
    
    rprint(f"[cyan]Location history for '{char_name}':")
    for loc, ts in rows:
        rprint(f"- {loc} at {ts}")