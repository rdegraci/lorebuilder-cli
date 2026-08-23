
"""
lore.py

Lore-related logic, ChromaDB and embedding initializations relevant for lore functions.
Exports: add_lore, generate_lore, store_generated_lore, and other lore commands.
Required: Must call init_lore(config, chroma_collection, embedder, llm_api_key, chat_history) before use.
"""

import json
import random
import traceback
from typing import Dict, List, Optional, Any, Union
from rich import print as rprint
import litellm
from datetime import datetime
from llm_utils import extract_completion_text
from constants import (
    MIN_LORE_ID,
    MAX_LORE_ID,
    DEFAULT_MAX_TOKENS,
    DEFAULT_QUERY_RESULTS,
    DISPLAY_TEXT_LIMIT,
    MIN_QUERY_LENGTH,
    ERROR_LORE_SERVICE_NOT_INITIALIZED,
    SUCCESS_LORE_ADDED,
    SUCCESS_LORE_STORED,
    SUCCESS_LORE_DELETED,
    ERROR_ADDING_LORE,
    ERROR_GENERATING_LORE,
    ERROR_STORING_LORE,
    ERROR_QUERYING_LORE,
    ERROR_LISTING_LORE,
    ERROR_DELETING_LORE,
    WARNING_NO_LORE_TO_STORE,
    WARNING_NO_LORE_FOUND,
    INFO_NO_EXISTING_LORE,
    USAGE_ADD_LORE,
    USAGE_GENERATE_LORE,
    USAGE_QUERY_LORE,
    USAGE_DELETE_LORE,
    DEFAULT_LORE_SYSTEM_PROMPT,
    DEFAULT_LORE_FALLBACK_CONTEXT,
    LORE_MODULE_INITIALIZED
)

class LoreService:
    """Service class for managing lore entries with ChromaDB and LLM integration."""
    
    def __init__(
        self, 
        config: Dict[str, Any], 
        chroma_collection: Any, 
        embedder: Any, 
        llm_api_key: str, 
        chat_history: Any
    ) -> None:
        """Initialize the LoreService with required dependencies.
        
        Args:
            config: Application configuration dictionary
            chroma_collection: ChromaDB collection for storing lore
            embedder: Document embedding function
            llm_api_key: API key for language model access
            chat_history: Chat history module for character interactions
        """
        self.config = config
        self.chroma_collection = chroma_collection
        self.embedder = embedder
        self.llm_api_key = llm_api_key
        self.chat_history = chat_history
        rprint(LORE_MODULE_INITIALIZED)
    
    def _generate_lore_id(self) -> str:
        """Generate a random lore ID.
        
        Returns:
            A string representation of a random integer ID
        """
        return str(random.randint(MIN_LORE_ID, MAX_LORE_ID))
    
    def _get_system_prompt(self, existing_lore: str = "") -> str:
        """Get the system prompt for lore generation with context replacement.
        
        Args:
            existing_lore: Existing lore context to include in prompt
            
        Returns:
            Formatted system prompt string
        """
        system_prompt = self.config.get(
            "lore_llm_system_prompt", 
            self.config.get("prompt_template", DEFAULT_LORE_SYSTEM_PROMPT)
        )
        
        if existing_lore:
            system_prompt = system_prompt.replace("{context}", existing_lore)
        else:
            system_prompt = system_prompt.replace(
                "{context}", 
                DEFAULT_LORE_FALLBACK_CONTEXT
            )
        
        return system_prompt
    
    def add_lore(self, args: List[str], context: Dict[str, Any]) -> None:
        """Add a lore entry to ChromaDB.
        
        Args:
            args: Command arguments containing the lore text
            context: Shared context dictionary
        """
        if not args:
            rprint(USAGE_ADD_LORE)
            return
        
        lore_text = " ".join(args)
        lore_id = self._generate_lore_id()
        
        try:
            # Generate embedding for the lore text
            embedding = self.embedder([lore_text])[0]
            
            # Add to ChromaDB collection
            self.chroma_collection.add(
                documents=[lore_text], 
                embeddings=[embedding], 
                ids=[lore_id],
                metadatas=[{"timestamp": datetime.now().isoformat(), "source": "user"}]
            )
            
            rprint(SUCCESS_LORE_ADDED.format(id=lore_id))
            context['last_generated_lore'] = lore_text
        except Exception as e:
            rprint(ERROR_ADDING_LORE.format(error=e))
    
    def generate_lore(self, args: List[str], context: Dict[str, Any]) -> None:
        """Generate new lore using LLM and config prompt.
        
        Args:
            args: Command arguments containing the prompt
            context: Shared context dictionary
        """
        if not args:
            rprint(USAGE_GENERATE_LORE)
            return
        
        prompt = " ".join(args)
        
        # Get relevant existing lore if available
        existing_lore = ""
        try:
            if len(prompt) > MIN_QUERY_LENGTH:
                results = self.query_lore_internal(prompt, 3)
                if results:
                    existing_lore = "\n\n".join(results)
        except Exception as e:
            rprint(f"[dim]Note: Could not retrieve existing lore context. {e}[/dim]")
        
        # Prepare system prompt with existing lore if available
        system_prompt = self._get_system_prompt(existing_lore)
        
        # Set up LLM request
        llm_args = {
            "model": self.config.get("lore_llm_model", self.config.get("llm_provider", "openai/gpt-4o-mini")),
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "api_key": self.llm_api_key,
            "max_tokens": DEFAULT_MAX_TOKENS
        }
        
        try:
            response = litellm.completion(**llm_args)
            generated = extract_completion_text(response)
            context['last_generated_lore'] = generated
            rprint(f"[green]Generated Lore:")
            rprint(f"{generated}")
        except Exception as e:
            rprint(ERROR_GENERATING_LORE.format(error=e))
    
    def store_generated_lore(self, args: List[str], context: Dict[str, Any]) -> None:
        """Store the last generated lore into ChromaDB.
        
        Args:
            args: Command arguments (unused)
            context: Shared context dictionary containing last_generated_lore
        """
        if not context.get("last_generated_lore"):
            rprint(WARNING_NO_LORE_TO_STORE)
            return
        
        lore_text = context["last_generated_lore"]
        lore_id = self._generate_lore_id()
        
        try:
            embedding = self.embedder([lore_text])[0]
            self.chroma_collection.add(
                documents=[lore_text], 
                embeddings=[embedding], 
                ids=[lore_id],
                metadatas=[{"timestamp": datetime.now().isoformat(), "source": "generated"}]
            )
            rprint(SUCCESS_LORE_STORED.format(id=lore_id))
        except Exception as e:
            rprint(ERROR_STORING_LORE.format(error=e))
    
    def query_lore_internal(self, query: str, n_results: int = DEFAULT_QUERY_RESULTS) -> List[str]:
        """Query relevant lore from the collection.
        
        Args:
            query: The search query text
            n_results: Number of results to return
            
        Returns:
            List of relevant lore text entries
        """
        # Let the ChromaDB collection handle the embedding internally
        results = self.chroma_collection.query(
            query_texts=[query],
            n_results=n_results
        )
        docs = results.get("documents", [[]])[0]
        return docs
    
    def query_lore(self, args: List[str], context: Dict[str, Any]) -> None:
        """Query relevant lore entries.
        
        Args:
            args: Command arguments containing the query
            context: Shared context dictionary
        """
        if not args:
            rprint(USAGE_QUERY_LORE)
            return
        
        query = " ".join(args)
        
        try:
            docs = self.query_lore_internal(query)
            
            if docs:
                rprint(f"[cyan]Relevant Lore Entries:")
                for i, d in enumerate(docs, 1):
                    rprint(f"[bold]Entry {i}:[/bold] {d}")
            else:
                rprint(WARNING_NO_LORE_FOUND)
        except Exception as e:
            rprint(ERROR_QUERYING_LORE.format(error=e))
    
    def list_all_lore(self, args: List[str], context: Dict[str, Any]) -> None:
        """List all lore entries in the system.
        
        Args:
            args: Command arguments (unused)
            context: Shared context dictionary
        """
        try:
            # Get all documents from collection
            results = self.chroma_collection.get()
            docs = results.get("documents", [])
            ids = results.get("ids", [])
            
            if not docs:
                rprint(INFO_NO_EXISTING_LORE)
                return
                
            rprint(f"[cyan]All Lore Entries ([bold]{len(docs)}[/bold] total):")
            for i, (doc_id, doc) in enumerate(zip(ids, docs), 1):
                # Truncate long entries for display
                display_text = doc[:DISPLAY_TEXT_LIMIT] + "..." if len(doc) > DISPLAY_TEXT_LIMIT else doc
                rprint(f"[bold]{i}. ID {doc_id}:[/bold] {display_text}")
                
            rprint("[dim]Use query_lore to find specific entries.")
        except Exception as e:
            rprint(ERROR_LISTING_LORE.format(error=e))
    
    def delete_lore(self, args: List[str], context: Dict[str, Any]) -> None:
        """Delete a specific lore entry by ID.
        
        Args:
            args: Command arguments containing the lore ID
            context: Shared context dictionary
        """
        if not args:
            rprint(USAGE_DELETE_LORE)
            return
            
        lore_id = args[0]
        
        try:
            self.chroma_collection.delete(ids=[lore_id])
            rprint(SUCCESS_LORE_DELETED.format(id=lore_id))
        except Exception as e:
            rprint(ERROR_DELETING_LORE.format(error=e))


# Global instance for backward compatibility
_lore_service: Optional[LoreService] = None

def init_lore(config: Dict[str, Any], chroma_collection: Any, embedder: Any, llm_api_key: str, chat_history: Any) -> None:
    """Initialize the global lore service with dependencies.
    
    Args:
        config: Application configuration dictionary
        chroma_collection: ChromaDB collection for storing lore
        embedder: Document embedding function
        llm_api_key: API key for language model access
        chat_history: Chat history module for character interactions
    """
    global _lore_service
    _lore_service = LoreService(config, chroma_collection, embedder, llm_api_key, chat_history)

def add_lore(args: List[str], context: Dict[str, Any]) -> None:
    """Command handler for adding lore entry to ChromaDB.
    
    Args:
        args: Command arguments containing the lore text
        context: Shared context dictionary
    """
    if _lore_service is None:
        rprint(ERROR_LORE_SERVICE_NOT_INITIALIZED)
        return
    _lore_service.add_lore(args, context)

def generate_lore(args: List[str], context: Dict[str, Any]) -> None:
    """Command handler: Generate new lore using LLM and config prompt.
    
    Args:
        args: Command arguments containing the prompt
        context: Shared context dictionary
    """
    if _lore_service is None:
        rprint(ERROR_LORE_SERVICE_NOT_INITIALIZED)
        return
    _lore_service.generate_lore(args, context)

def store_generated_lore(args: List[str], context: Dict[str, Any]) -> None:
    """Command handler: Store the last generated lore into ChromaDB.
    
    Args:
        args: Command arguments (unused)
        context: Shared context dictionary containing last_generated_lore
    """
    if _lore_service is None:
        rprint(ERROR_LORE_SERVICE_NOT_INITIALIZED)
        return
    _lore_service.store_generated_lore(args, context)

def query_lore_internal(query: str, n_results: int = DEFAULT_QUERY_RESULTS) -> List[str]:
    """Internal helper function to query relevant lore.
    
    Args:
        query: The search query text
        n_results: Number of results to return
        
    Returns:
        List of relevant lore text entries
    """
    if _lore_service is None:
        return []
    return _lore_service.query_lore_internal(query, n_results)

def query_lore(args: List[str], context: Dict[str, Any]) -> None:
    """Command handler: Query relevant lore.
    
    Args:
        args: Command arguments containing the query
        context: Shared context dictionary
    """
    if _lore_service is None:
        rprint(ERROR_LORE_SERVICE_NOT_INITIALIZED)
        return
    _lore_service.query_lore(args, context)

def list_all_lore(args: List[str], context: Dict[str, Any]) -> None:
    """Command handler: List all lore entries in the system.
    
    Args:
        args: Command arguments (unused)
        context: Shared context dictionary
    """
    if _lore_service is None:
        rprint(ERROR_LORE_SERVICE_NOT_INITIALIZED)
        return
    _lore_service.list_all_lore(args, context)

def delete_lore(args: List[str], context: Dict[str, Any]) -> None:
    """Command handler: Delete a specific lore entry by ID.
    
    Args:
        args: Command arguments containing the lore ID
        context: Shared context dictionary
    """
    if _lore_service is None:
        rprint(ERROR_LORE_SERVICE_NOT_INITIALIZED)
        return
    _lore_service.delete_lore(args, context)


