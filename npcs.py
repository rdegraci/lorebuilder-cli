
"""
Helper functions for NPC management, lookup, and plausible population for scenes.

This version has been simplified: all scene/location-aware logic has been removed.
NPC suggestions are now drawn solely from a default list, with optional basic context.
Functions depending on locations or scene-specific knowledge have been removed.
"""
import random
import json

def plausible_npcs_for_scene(scene_name=None, extra_context=None):
    """
    Returns a list of plausible NPCs using a simple default pool, ignoring location/scene input.

    Args:
        scene_name (str, optional): Formerly used for location lookups; ignored now.
        extra_context (str, optional): Context or tags to optionally influence selection (not implemented).

    Returns:
        list: List of NPC name strings.
    """
    # All location- and scene-specific handling removed.
    default_npcs = [
        "Wandering Bard",
        "Curious Merchant",
        "Silent Watcher",
        "Ancient Statue",
        "Mira"
    ]
    # No scene_key or lookups; use only the default.
    # Optionally shuffle or trim for variety
    return random.sample(default_npcs, k=min(3, len(default_npcs)))


# Function get_present_characters and all location/scene-specific code has been removed as per instructions.
