"""
lore.py

Lore-related logic, ChromaDB and embedding initializations relevant for lore functions.
Exports: add_lore, generate_lore, store_generated_lore, and other lore commands.
Required: Must call init_lore(config, chroma_collection, embedder, llm_api_key, chat_history) before use.
"""

import json
import random
import traceback
from rich import print as rprint
import litellm
from datetime import datetime

# Globals initialized via init_lore
_config = None
_chroma_collection = None
_embedder = None
_llm_api_key = None
_chat_history = None

def init_lore(config, chroma_collection, embedder, llm_api_key, chat_history):
    """
    Set up dependencies for lore module (embedding, ChromaDB, config, API keys, chat_history).
    Call this from app.py at startup before invoking any lore functions.
    
    Args:
        config (dict): Application configuration
        chroma_collection: ChromaDB collection for storing lore
        embedder: Document embedding function
        llm_api_key (str): API key for language model access
        chat_history: Chat history module for character interactions
    """
    global _config, _chroma_collection, _embedder, _llm_api_key, _chat_history
    _config = config
    _chroma_collection = chroma_collection
    _embedder = embedder
    _llm_api_key = llm_api_key
    _chat_history = chat_history
    rprint("[dim]Lore module initialized.[/dim]")

def add_lore(args, context):
    """
    Command handler for adding lore entry to ChromaDB.
    Usage: add_lore <lore_text>
    
    Args:
        args (list): Command arguments containing the lore text
        context (dict): Shared context dictionary
    """
    if not args:
        rprint("[yellow]Usage: add_lore <lore_text>")
        return
    
    lore_text = " ".join(args)
    lore_id = str(random.randint(100000, 999999))
    
    try:
        # Generate embedding for the lore text
        embedding = _embedder.embed_documents([lore_text])[0]
        
        # Add to ChromaDB collection
        _chroma_collection.add(
            documents=[lore_text], 
            embeddings=[embedding], 
            ids=[lore_id],
            metadatas=[{"timestamp": datetime.now().isoformat(), "source": "user"}]
        )
        
        rprint(f"[green]Lore added with id {lore_id}.")
        context['last_generated_lore'] = lore_text
    except Exception as e:
        traceback.print_exc()
        rprint(f"[red]Error adding lore: {e}")

def generate_lore(args, context):
    """
    Command handler: Generate new lore using LLM and config prompt.
    Usage: generate_lore <user_prompt>
    
    Args:
        args (list): Command arguments containing the prompt
        context (dict): Shared context dictionary
    """
    if not args:
        rprint("[yellow]Usage: generate_lore <user_prompt>")
        return
    
    prompt = " ".join(args)
    
    # Get relevant existing lore if available
    existing_lore = ""
    try:
        if len(prompt) > 3:  # Don't search for very short prompts
            results = query_lore_internal(prompt, 3)
            if results:
                existing_lore = "\n\n".join(results)
    except Exception as e:
        rprint(f"[dim]Note: Could not retrieve existing lore context. {e}[/dim]")
    
    # Prepare system prompt with existing lore if available
    system_prompt = _config.get("lore_llm_system_prompt", _config.get("prompt_template", "You are a creative worldbuilder."))
    if existing_lore:
        # Replace {context} placeholder with existing lore
        system_prompt = system_prompt.replace("{context}", existing_lore)
    else:
        # If no existing lore, replace with empty context note
        system_prompt = system_prompt.replace("{context}", "(No existing world lore found. Create something new.)")
    
    # Set up LLM request
    llm_args = {
        "model": _config.get("lore_llm_model", _config.get("llm_provider", "openai/gpt-4o-mini")),
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "api_key": _llm_api_key,
        "max_tokens": 512
    }
    
    try:
        response = litellm.completion(**llm_args)
        generated = response["choices"][0]["message"]["content"]
        context['last_generated_lore'] = generated
        rprint(f"[green]Generated Lore:")
        rprint(f"{generated}")
    except Exception as e:
        traceback.print_exc()
        rprint(f"[red]Error generating lore: {e}")

def store_generated_lore(args, context):
    """
    Command handler: Store the last generated lore into ChromaDB.
    Usage: store_generated_lore
    
    Args:
        args (list): Command arguments (unused)
        context (dict): Shared context dictionary containing last_generated_lore
    """
    if not context.get("last_generated_lore"):
        rprint("[yellow]No generated lore to store. Use generate_lore first.")
        return
    
    lore_text = context["last_generated_lore"]
    lore_id = str(random.randint(100000, 999999))
    
    try:
        embedding = _embedder.embed_documents([lore_text])[0]
        _chroma_collection.add(
            documents=[lore_text], 
            embeddings=[embedding], 
            ids=[lore_id],
            metadatas=[{"timestamp": datetime.now().isoformat(), "source": "generated"}]
        )
        rprint(f"[green]Stored generated lore with id {lore_id}.")
    except Exception as e:
        traceback.print_exc()
        rprint(f"[red]Error storing generated lore: {e}")

def query_lore_internal(query, n_results=5):
    """
    Internal helper function to query relevant lore.
    
    Args:
        query (str): The search query text
        n_results (int): Number of results to return
        
    Returns:
        list: List of relevant lore text entries
    """
    # Let the ChromaDB collection handle the embedding internally
    results = _chroma_collection.query(
        query_texts=[query],
        n_results=n_results
    )
    docs = results.get("documents", [[]])[0]
    return docs

def query_lore(args, context):
    """
    Command handler: Query relevant lore.
    Usage: query_lore <query>
    
    Args:
        args (list): Command arguments containing the query
        context (dict): Shared context dictionary
    """
    if not args:
        rprint("[yellow]Usage: query_lore <query>")
        return
    
    query = " ".join(args)
    
    try:
        docs = query_lore_internal(query)
        
        if docs:
            rprint(f"[cyan]Relevant Lore Entries:")
            for i, d in enumerate(docs, 1):
                rprint(f"[bold]Entry {i}:[/bold] {d}")
        else:
            rprint("[dim]No relevant lore found.")
    except Exception as e:
        traceback.print_exc()
        rprint(f"[red]Error querying lore: {e}")

def list_all_lore(args, context):
    """
    Command handler: List all lore entries in the system.
    Usage: list_all_lore
    
    Args:
        args (list): Command arguments (unused)
        context (dict): Shared context dictionary
    """
    try:
        # Get all documents from collection
        results = _chroma_collection.get()
        docs = results.get("documents", [])
        ids = results.get("ids", [])
        
        if not docs:
            rprint("[dim]No lore entries found in the system.")
            return
            
        rprint(f"[cyan]All Lore Entries ([bold]{len(docs)}[/bold] total):")
        for i, (doc_id, doc) in enumerate(zip(ids, docs), 1):
            # Truncate long entries for display
            display_text = doc[:100] + "..." if len(doc) > 100 else doc
            rprint(f"[bold]{i}. ID {doc_id}:[/bold] {display_text}")
            
        rprint("[dim]Use query_lore to find specific entries.")
    except Exception as e:
        traceback.print_exc()
        rprint(f"[red]Error listing lore: {e}")

def delete_lore(args, context):
    """
    Command handler: Delete a specific lore entry by ID.
    Usage: delete_lore <lore_id>
    
    Args:
        args (list): Command arguments containing the lore ID
        context (dict): Shared context dictionary
    """
    if not args:
        rprint("[yellow]Usage: delete_lore <lore_id>")
        return
        
    lore_id = args[0]
    
    try:
        _chroma_collection.delete(ids=[lore_id])
        rprint(f"[green]Deleted lore entry with ID {lore_id}.")
    except Exception as e:
        traceback.print_exc()
        rprint(f"[red]Error deleting lore: {e}")