"""
Helper functions for NPC management, lookup, and plausible population for scenes.
"""
import random
import json

def plausible_npcs_for_scene(scene_name, extra_context=None):
    """
    Returns a list of plausible NPCs for a scene, using stored lore or basic LLM-style generation.

    Args:
        scene_name (str): Name of the scene/location.
        extra_context (str, optional): Add world context or tags.

    Returns:
        list: List of NPC name strings.
    """
    # Example: for now, provide a small pool, expand later with LLM
    npcs_by_scene = {
        "Ancient Hall": ["Mira", "Old Caretaker", "Secretive Scholar"],
        "Overgrown Library": ["Eris the Librarian", "Dusty Golem"],
        "Mysterious Clearing": ["Lost Child", "Wandering Ranger", "Sprite"],
        "Twilight Glade": ["Wistful Dryad", "Passing Merchant"],
        "Ruined Watchtower": ["Giant Rat", "Watchful Spirit", "Scout"],
        "Shadowed Woods": ["Glowing Fox", "Shadow Stalker", "Wise Owl"],
        # Demo for universal fallback
        "default": [
            "Wandering Bard", "Curious Merchant", "Silent Watcher",
            "Ancient Statue", "Mira"  # added Mira so one returns if she present
        ]
    }
    # Pick from specific if exists, otherwise random from default
    scene_key = scene_name.split('#')[0].strip() if '#' in scene_name else scene_name.strip()
    npcs = npcs_by_scene.get(scene_key)
    if not npcs:
        npcs = random.sample(npcs_by_scene["default"], k=min(3, len(npcs_by_scene["default"])))
    # Add context-based shuffling if needed (expandable)
    return npcs

def get_present_characters(location_id, exclude=None, db_connection_fn=None):
    """
    Returns a list of character names currently recorded at the specified location.

    Args:
        location_id (str): Location UUID.
        exclude (str or list): Names to exclude from NPC output.
        db_connection_fn (function, optional): Function to get db connection.

    Returns:
        list: Character names.
    """
    if exclude is None:
        exclude = []
    elif isinstance(exclude, str):
        exclude = [exclude]
    if not db_connection_fn:
        raise ValueError("You must supply a db_connection_fn to access the DB.")
    conn = db_connection_fn()
    c = conn.cursor()
    c.execute("SELECT character_name FROM character_location WHERE location_id = ?", (location_id,))
    results = [row[0] for row in c.fetchall() if row[0] not in exclude]
    conn.close()
    return results
