
"""
Helper functions for NPC management, lookup, and plausible population for scenes.

This version has been simplified: all scene/location-aware logic has been removed.
NPC suggestions are now drawn solely from a default list, with optional basic context.
Functions depending on locations or scene-specific knowledge have been removed.
"""
import random
import json
from typing import List, Optional, Dict, Any, Union


class NPCService:
    """
    Service class for managing NPCs (Non-Player Characters).
    
    Provides functionality for NPC selection, management, and generation
    with configurable selection strategies and robust error handling.
    """
    
    # Default NPCs pool as class constant
    DEFAULT_NPCS = [
        "Wandering Bard",
        "Curious Merchant",
        "Silent Watcher",
        "Ancient Statue",
        "Mira"
    ]
    
    def __init__(self, npcs: Optional[List[str]] = None):
        """
        Initialize the NPCService with a list of NPCs.
        
        Args:
            npcs: Optional list of NPC names. If None, uses DEFAULT_NPCS.
        """
        self._npcs = npcs.copy() if npcs is not None else self.DEFAULT_NPCS.copy()
    
    def plausible_npcs_for_scene(
        self, 
        scene_name: Optional[str] = None, 
        extra_context: Optional[str] = None,
        count: int = 3,
        strategy: str = "random"
    ) -> List[str]:
        """
        Returns a list of plausible NPCs using the configured pool.

        Args:
            scene_name: Formerly used for location lookups; ignored now.
            extra_context: Context or tags to optionally influence selection (not implemented).
            count: Number of NPCs to return (default: 3).
            strategy: Selection strategy ("random", "sequential", "all").

        Returns:
            List of NPC name strings.
            
        Raises:
            ValueError: If count is negative or strategy is invalid.
        """
        if count < 0:
            raise ValueError("Count must be non-negative")
        
        if not self._npcs:
            return []
        
        if strategy == "random":
            return random.sample(self._npcs, k=min(count, len(self._npcs)))
        elif strategy == "sequential":
            return self._npcs[:min(count, len(self._npcs))]
        elif strategy == "all":
            return self._npcs.copy()
        else:
            raise ValueError(f"Invalid strategy: {strategy}. Must be 'random', 'sequential', or 'all'")
    
    def add_npc(self, npc_name: str) -> bool:
        """
        Add an NPC to the pool.
        
        Args:
            npc_name: Name of the NPC to add.
            
        Returns:
            True if NPC was added, False if it already exists.
            
        Raises:
            ValueError: If npc_name is empty or None.
        """
        if not npc_name or not npc_name.strip():
            raise ValueError("NPC name cannot be empty")
        
        npc_name = npc_name.strip()
        if npc_name not in self._npcs:
            self._npcs.append(npc_name)
            return True
        return False
    
    def remove_npc(self, npc_name: str) -> bool:
        """
        Remove an NPC from the pool.
        
        Args:
            npc_name: Name of the NPC to remove.
            
        Returns:
            True if NPC was removed, False if it didn't exist.
        """
        if npc_name in self._npcs:
            self._npcs.remove(npc_name)
            return True
        return False
    
    def get_npc_by_name(self, npc_name: str) -> Optional[str]:
        """
        Get an NPC by exact name match.
        
        Args:
            npc_name: Name of the NPC to find.
            
        Returns:
            The NPC name if found, None otherwise.
        """
        return npc_name if npc_name in self._npcs else None
    
    def list_all_npcs(self) -> List[str]:
        """
        Get a list of all NPCs in the pool.
        
        Returns:
            Copy of the current NPC list.
        """
        return self._npcs.copy()
    
    def generate_random_npc(self) -> Dict[str, Any]:
        """
        Generate a random NPC with basic attributes.
        
        Returns:
            Dictionary containing NPC data with name and basic attributes.
            
        Raises:
            RuntimeError: If no NPCs are available in the pool.
        """
        if not self._npcs:
            raise RuntimeError("No NPCs available in the pool")
        
        name = random.choice(self._npcs)
        
        # Basic attributes for generated NPC
        attributes = {
            "name": name,
            "disposition": random.choice(["friendly", "neutral", "hostile", "mysterious"]),
            "activity": random.choice(["standing", "walking", "sitting", "working", "watching"]),
            "availability": random.choice(["available", "busy", "unavailable"])
        }
        
        return attributes
    
    def get_npc_count(self) -> int:
        """
        Get the total number of NPCs in the pool.
        
        Returns:
            Number of NPCs currently in the pool.
        """
        return len(self._npcs)
    
    def clear_npcs(self) -> None:
        """
        Clear all NPCs from the pool.
        """
        self._npcs.clear()
    
    def reset_to_defaults(self) -> None:
        """
        Reset the NPC pool to the default NPCs.
        """
        self._npcs = self.DEFAULT_NPCS.copy()


# Global NPCService instance for backward compatibility
_npc_service = NPCService()


def plausible_npcs_for_scene(scene_name: Optional[str] = None, extra_context: Optional[str] = None) -> List[str]:
    """
    Returns a list of plausible NPCs using a simple default pool, ignoring location/scene input.

    Args:
        scene_name: Formerly used for location lookups; ignored now.
        extra_context: Context or tags to optionally influence selection (not implemented).

    Returns:
        List of NPC name strings.
    """
    return _npc_service.plausible_npcs_for_scene(scene_name, extra_context)


# Function get_present_characters and all location/scene-specific code has been removed as per instructions.
