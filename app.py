
import yaml
import chromadb
from chromadb.utils import embedding_functions
import litellm
from rich import print as rprint
from datetime import datetime
import os
from dotenv import load_dotenv
import chat_history
import sqlite3
import uuid
import json
import random
import traceback   # [fix 4] Add import for traceback for debug reporting.

os.environ["TOKENIZERS_PARALLELISM"] = "false"

# --- Load environment variables ---
load_dotenv()

# --- Load Config ---
with open("app.yaml") as f:
    config = yaml.safe_load(f)

# --- Ensure llm_api_key is read from environment ---
if not os.getenv("LLM_API_KEY"):
    raise EnvironmentError("LLM_API_KEY not set in .env or environment.")
llm_api_key = os.getenv("LLM_API_KEY")

# --- Init Embedding ---
embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=config["embedding_model"]
)

# --- Init ChromaDB ---
client = chromadb.PersistentClient(path=config["chromadb_path"])
collection = client.get_or_create_collection("lore", embedding_function=embedder)

# --- Init chat DB ---
chat_history.initialize_db()

# --- Init SQLite for Location Tracking ---
def initialize_location_db():
    """Initializes the SQLite database for storing character-location mapping.

    Creates tables for character_location and idempotent location_entries.
    """
    conn = sqlite3.connect(config.get("sqlite_path", "state.db"))
    c = conn.cursor()
    # Map per session or per character last location
    c.execute("""
    CREATE TABLE IF NOT EXISTS character_location (
        character_name TEXT PRIMARY KEY,
        location_id TEXT,
        timestamp TEXT
    )
    """)
    # Stores previous canonical location lore:
    c.execute("""
    CREATE TABLE IF NOT EXISTS location_entries (
        location_id TEXT PRIMARY KEY,
        display_name TEXT,
        description TEXT,
        exits TEXT, -- JSON array or string format
        timestamp TEXT,
        last_saved_canonical_id TEXT
    )
    """)
    conn.commit()
    conn.close()

def get_db_connection():
    """Returns a connection to the SQLite state database."""
    return sqlite3.connect(config.get("sqlite_path", "state.db"))

initialize_location_db()

def assign_or_get_current_location(character_name):
    """Assigns or retrieves current location for a given character.

    Args:
        character_name (str): Name of the character/session.

    Returns:
        tuple: (location_id, display_name)
    """
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT location_id FROM character_location WHERE character_name = ?", (character_name,))
    row = c.fetchone()
    if row and row[0]:
        location_id = row[0]
        # Try to get display_name for this location:
        c.execute("SELECT display_name FROM location_entries WHERE location_id = ?", (location_id,))
        dnrow = c.fetchone()
        display_name = dnrow[0] if dnrow else None
        conn.close()
        return location_id, display_name
    else:
        # Generate a new location name (simple random for now)
        location_words = [
            "Mysterious Clearing", "Ancient Hall", "Forgotten Cave",
            "Overgrown Library", "Whispering Meadow", "Shadowed Woods",
            "Crystal Lake", "Ruined Watchtower", "Hidden Alcove",
            "Silent Grove", "Twilight Glade", "Thunder Plateau"
        ]
        display_name = random.choice(location_words) + " #" + str(random.randint(1000, 9999))
        location_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        c.execute(
            "INSERT INTO character_location (character_name, location_id, timestamp) VALUES (?, ?, ?)",
            (character_name, location_id, timestamp)
        )
        c.execute(
            "INSERT OR IGNORE INTO location_entries (location_id, display_name, description, exits, timestamp, last_saved_canonical_id) VALUES (?, ?, ?, ?, ?, ?)",
            (location_id, display_name, "", "[]", timestamp, None)
        )
        conn.commit()
        conn.close()
        return location_id, display_name

def update_character_location(character_name, location_id):
    """Sets the current location_id for a character and updates time.

    Args:
        character_name (str): Character name.
        location_id (str): New location ID.
    """
    conn = get_db_connection()
    timestamp = datetime.utcnow().isoformat()
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO character_location (character_name, location_id, timestamp) VALUES (?, ?, ?)",
        (character_name, location_id, timestamp)
    )
    conn.commit()
    conn.close()

def get_location_lore_from_chromadb(location_id):
    """Retrieves canonical lore for the location from ChromaDB.

    Args:
        location_id (str): Location unique ID.

    Returns:
        dict or None: Metadata dict, or None if not found.
    """
    # ChromaDB can only accept a single operator/field in 'where'. Only use 'metadata.location_id' here.
    results = collection.query(
        query_texts=[location_id],
        n_results=5,
        where={"metadata.location_id": location_id}
        # Cannot do: "where={"metadata.location_id": ..., "metadata.canonical": True}"
    )
    try:
        docs = results['documents'][0]
        md = results['metadatas'][0]
    except Exception:
        docs = []
        md = []
    if not docs:
        return None
    # Post-filter in Python for canonical entries only
    for d, m in zip(docs, md):
        if m and m.get("canonical", False):
            dct = dict(m)
            dct["description"] = d
            return dct
    return None

def add_or_update_location_entry(location_id, display_name, description, exits, canonical=True, created_by="LLM", tags=None):
    """Appends a new location lore entry to ChromaDB and records in SQLite location_entries table.

    Ensures only one entry with canonical=true per location.

    Args:
        location_id (str): Location UUID.
        display_name (str): Name to show to player.
        description (str): Full scene description.
        exits (list or str): List of exits (in text, or JSON-encoded).
        canonical (bool): Whether this entry is canonical.
        created_by (str): Who or what authored this lore.
        tags (list): Optional tags.
    """
    if isinstance(exits, str):
        try:
            exits_list = json.loads(exits)
        except Exception:
            exits_list = [exits]
    else:
        exits_list = exits

    timestamp = datetime.utcnow().isoformat()
    metadata = {
        "location_id": location_id,
        "display_name": display_name,
        "description": description,
        "exits": exits_list,
        "created_by": created_by,
        "timestamp": timestamp,
        "canonical": canonical,
        "tags": tags or [],
    }
    # ChromaDB can only filter on a single field/operator in 'where'; only use 'metadata.location_id'
    results = collection.query(
        query_texts=[location_id], n_results=20, where={"metadata.location_id": location_id}
        # No "metadata.canonical" filter here, must filter canonical in Python after this
    )
    new_id = str(uuid.uuid4())
    metadatas = results.get("metadatas", [[]])[0]
    doc_ids = results.get("ids", [[]])[0]
    if canonical:
        # Post-filter in Python for canonical versions
        for meta, did in zip(metadatas, doc_ids):
            if meta.get("canonical", False):
                old = dict(meta)
                old["canonical"] = False
                # Add new noncanonical version of the same doc to collection with different id
                collection.add(
                    documents=[meta.get("description", "")],
                    metadatas=[old],
                    ids=[str(uuid.uuid4())]
                )
    # Append new canonical entry
    collection.add(
        documents=[description],
        metadatas=[metadata],
        ids=[new_id]
    )
    # Record the entry in SQLite as well as for faster lookup
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        """
        INSERT OR REPLACE INTO location_entries
        (location_id, display_name, description, exits, timestamp, last_saved_canonical_id)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            location_id,
            display_name,
            description,
            json.dumps(exits_list),
            timestamp,
            new_id if canonical else None,
        )
    )
    conn.commit()
    conn.close()


def get_location_entry(location_id):
    """Fetches display name, description, and exits for a location from SQLite.

    Args:
        location_id (str): Location unique ID.

    Returns:
        dict or None: {'display_name', 'description', 'exits'} if found.
    """
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "SELECT display_name, description, exits FROM location_entries WHERE location_id = ?",
        (location_id,)
    )
    row = c.fetchone()
    conn.close()
    if row:
        try:
            exits = json.loads(row[2]) if row[2] else []
        except Exception:
            exits = []
        return {"display_name": row[0], "description": row[1], "exits": exits}
    else:
        return None

def generate_location_description_and_exits(display_name, additional_context=None):
    """Uses LLM to generate a location description and possible exits.

    Args:
        display_name (str): Location name for display.
        additional_context (str, optional): Extra context, e.g., character's inventory, etc.

    Returns:
        tuple: (description, exits)
    """
    # The JSON braces below are doubled ({{ and }}), so .format() does not treat them as replacement fields.
    # This prevents accidental formatting errors and renders one literal brace in the prompt sent to the LLM.
    system_prompt = (
        "You are a creative, evocative storyteller. Generate a vivid, brief fantasy scene description for the following location, "
        "plus a list of possible exits, in the style of interactive fiction. Respond in JSON format:\n"
        '{{\n"description": "...",\n"exits": ["exit1", "exit2", ...]\n}}\n\n'
        "Location: {display_name}\n"
    )
    if additional_context:
        system_prompt += f"\nAdditional context: {additional_context}\n"
    prompt = system_prompt.format(display_name=display_name)
    output = call_llm(prompt=prompt)
    try:
        parsed = json.loads(output)
        desc = parsed["description"]
        exits = parsed["exits"]
        if not isinstance(exits, list):
            exits = [str(exits)]
    except Exception:
        # Print the raw LLM output for debugging
        print("[DEBUG] LLM raw output:", repr(output))
        desc = None
        exits = None
        # Try to robustly extract description and exits using substring finding if possible
        # Check for '"description"' or 'description:' as a possible signal
        desc_start = -1
        desc_end = -1
        exits_start = -1
        # Try JSON style: "description": or fallback YAML style: description:
        if '"description"' in output:
            desc_key = '"description"'
            desc_start = output.find(desc_key)
            if desc_start != -1:
                after_colon = output.find(":", desc_start)
                # Find the first quote after the colon for the value
                val_start = output.find('"', after_colon+1)
                val_end = output.find('"', val_start+1)
                if val_start != -1 and val_end != -1:
                    desc = output[val_start+1:val_end].strip()
        elif 'description:' in output:
            desc_key = 'description:'
            desc_start = output.find(desc_key)
            if desc_start != -1:
                # Value starts after colon, could be quoted or not
                after_colon = desc_start + len(desc_key)
                tmp = output[after_colon:].lstrip()
                # Check for quote open
                if tmp and tmp[0] == '"':
                    val_end = tmp.find('"', 1)
                    if val_end != -1:
                        desc = tmp[1:val_end].strip()
                else:
                    nl = tmp.find('\n')
                    if nl == -1:
                        desc = tmp.strip()
                    else:
                        desc = tmp[:nl].strip()
        # Find exits
        if '"exits"' in output:
            exits_key = '"exits"'
            ekey_start = output.find(exits_key)
            if ekey_start != -1:
                col_e = output.find(":", ekey_start)
                arr_start = output.find('[', col_e)
                arr_end = output.find(']', arr_start)
                if arr_start != -1 and arr_end != -1:
                    arr_str = output[arr_start + 1:arr_end]
                    # Parse as array parts
                    exits = [e.strip().strip('"').strip("'") for e in arr_str.split(",") if e.strip().strip('"').strip("'")]
        elif 'exits:' in output:
            exits_key = 'exits:'
            ekey_start = output.find(exits_key)
            if ekey_start != -1:
                after_colon = ekey_start + len(exits_key)
                subset = output[after_colon:].lstrip()
                # If it starts with [ try to parse list
                if subset and subset[0] == '[':
                    arr_end = subset.find(']')
                    if arr_end != -1:
                        arr_str = subset[1:arr_end]
                        exits = [e.strip().strip('"').strip("'") for e in arr_str.split(",") if e.strip().strip('"').strip("'")]
                else:
                    # Split on comma or take all till next line
                    nl = subset.find('\n')
                    one_line_exits = subset[:nl] if nl != -1 else subset
                    exits = [e.strip().strip('"').strip("'") for e in one_line_exits.split(",") if e.strip().strip('"').strip("'")]
        # If still not found, fallback to splitting on 'Exits:'
        if desc is None or not desc:
            if 'Exits:' in output:
                split_desc = output.split('Exits:')
                desc = split_desc[0].strip()
                if len(split_desc) > 1:
                    exits_raw = split_desc[1].strip()
                    # Attempt comma splitting or line splitting
                    if ',' in exits_raw:
                        exits = [e.strip() for e in exits_raw.split(",") if e.strip()]
                    else:
                        exits = [e.strip() for e in exits_raw.split() if e.strip()]
            else:
                desc = output.strip()
        if exits is None or not exits:
            # Try to detect an exits line
            lines = output.split("\n")
            for line in lines:
                if line.lower().startswith("exits:"):
                    exval = line[len("exits:"):].strip()
                    if "," in exval:
                        exits = [e.strip() for e in exval.split(",") if e.strip()]
                    else:
                        exits = [exval] if exval else []
            # If still not found, minimal fallback
            if exits is None or not exits:
                exits = ['Unknown']
        # Always ensure desc and exits are stripped and properly set
        # [fix 1] Guarantee desc is always a non-None string and exits a non-empty list of strings.
        if desc is None or not isinstance(desc, str) or not desc.strip():
            desc = "You see a mysterious place, but its details are unclear."  # Safe fallback description
        else:
            desc = desc.strip()
        if exits is None or not isinstance(exits, list) or not exits or not any([str(e).strip() for e in exits]):
            exits = ['Unknown']  # Safe non-empty fallback for exits
        else:
            exits = [str(e).strip() for e in exits if str(e).strip()]
        # End fix 1 for exception fallback block
    # [fix 1] Ensure return desc as string, exits as non-empty list of strings always
    if desc is None or not isinstance(desc, str) or not desc.strip():
        desc = "You see a mysterious place, but its details are unclear."
    else:
        desc = desc.strip()
    if exits is None or not isinstance(exits, list) or not exits or not any([str(e).strip() for e in exits]):
        exits = ['Unknown']
    else:
        exits = [str(e).strip() for e in exits if str(e).strip()]
    return desc.strip(), exits


def look(character_name):
    """Handles the /look command, showing the current scene and exits for the character.

    This function retrieves or creates the current location and sets last_look_result.

    Args:
        character_name (str): The character/session identifier.

    Returns:
        dict: Information about the location including description, display_name, exits, location_id.
    """
    location_id, display_name = assign_or_get_current_location(character_name)
    # Try to get canonical lore for this location from ChromaDB
    lore_entry = get_location_lore_from_chromadb(location_id)
    if lore_entry:
        description = lore_entry.get("description", "")
        exits = lore_entry.get("exits", [])
        if isinstance(exits, str):
            try:
                exits = json.loads(exits)
            except Exception:
                exits = [exits]
    else:
        # Try to get any local lore for location
        entry = get_location_entry(location_id)
        description = entry["description"] if entry and entry["description"] else None
        exits = entry["exits"] if entry and entry["exits"] else []
        if not description or not exits:
            description, exits = generate_location_description_and_exits(display_name)
    # [fix 2] Guarantee description is always a string and exits always a non-empty list of strings for downstream safety.
    if description is None or not isinstance(description, str) or not description.strip():
        description = "This place seems indescribable. You sense its presence but its details escape you."
    else:
        description = description.strip()
    if exits is None or not isinstance(exits, list) or not exits or not any([str(e).strip() for e in exits]):
        exits = ['Unknown']
    else:
        exits = [str(e).strip() for e in exits if str(e).strip()]
    # END fix 2
    location_info = {
        "location_id": location_id,
        "display_name": display_name,
        "description": description,
        "exits": exits
    }
    global last_look_result
    last_look_result = location_info
    return location_info

def save_look(character_name):
    """Saves last_look_result to ChromaDB as canonical lore entry for the current location.

    Args:
        character_name (str): Name of the character/session.

    Returns:
        bool: True on success, False if there is no look result to save.
    """
    global last_look_result
    if not last_look_result:
        return False
    location_id = last_look_result["location_id"]
    display_name = last_look_result["display_name"]
    description = last_look_result["description"]
    exits = last_look_result["exits"]
    add_or_update_location_entry(
        location_id,
        display_name,
        description,
        exits,
        canonical=True,
        created_by="LLM",
        tags=["scene"]
    )
    # For idempotence, also update location_entries in SQLite
    update_character_location(character_name, location_id)
    return True

# --- Init LLM (with LiteLLM) ---
def call_llm(prompt=None, messages=None):
    if messages:  # chat-style
        response = litellm.completion(
            model=config["llm_provider"], api_key=llm_api_key, messages=messages
        )
        return response['choices'][0]['message']['content']
    elif prompt:
        response = litellm.completion(
            model=config["llm_provider"], api_key=llm_api_key, messages=[{"role": "system", "content": prompt}]
        )
        return response['choices'][0]['message']['content']
    else:
        raise ValueError("Either prompt or messages must be provided to call_llm.")

# --- Core Commands ---
def add_lore(text, metadata=None):
    """
    Add a lore string to the ChromaDB collection, ensuring non-empty metadata.
    """
    if not metadata or not isinstance(metadata, dict) or len(metadata) == 0:
        metadata = {"added": datetime.utcnow().isoformat()}
    collection.add(documents=[text], metadatas=[metadata], ids=[str(hash(text))])

def retrieve_lore(query, top_k=5):
    results = collection.query(query_texts=[query], n_results=top_k)
    return results['documents'][0] if results['documents'] else []

def generate_lore(query):
    context = retrieve_lore(query)
    prompt = config["prompt_template"].format(context="\n".join(context))
    return call_llm(prompt=prompt)

def store_generated_lore(text, metadata=None):
    add_lore(text, metadata)


# --- Multi-turn Chat As Character (with persistent history) ---
def chat_as_character(character_name: str, user_message: str, limit: int = 20):
    session_id = chat_history.get_or_create_session(character_name)
    history = chat_history.get_history(session_id, limit=limit)
    # Build messages for LLM: system = context, turns = user/assistant
    lore_context = '\n'.join(retrieve_lore(user_message))
    system_content = config["chat_prompt_template"].format(
        character_name=character_name, user_message="", context=lore_context
    )
    messages = [{"role": "system", "content": system_content}]
    for role, msg in history:
        llm_role = 'assistant' if role == 'character' else role
        messages.append({"role": llm_role, "content": msg})
    messages.append({"role": "user", "content": user_message})
    # Let LLM generate
    reply = call_llm(messages=messages)
    chat_history.add_message(session_id, 'user', user_message)
    chat_history.add_message(session_id, 'character', reply)
    return reply

# --- CLI Loop ---
def chat_loop():
    """
    Main command-line interface loop, with support for lore, world exploration, and chat commands.

    At start, shows the initial location for the last character from previous sessions.
    """
    rprint("[bold cyan]LoreBuilder CLI - Commands: add_lore, generate_lore, store_generated_lore, chat_as <character_name> <user_message>, /look, /save_look, /reset <character>, /history <character>, exit")
    last_generated_lore = ""
    global last_look_result
    last_look_result = None
    # At script start: show last location for last-used character (if any)
    try:
        # Attempt to discover last character/session
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT character_name FROM character_location ORDER BY timestamp DESC LIMIT 1")
        row = c.fetchone()
        conn.close()
        if row:
            first_char = row[0]
            scene_info = look(first_char)
            rprint(f"[bold green]Restored location for '{first_char}':")
            rprint(f"[bold magenta]{scene_info['display_name']}[/bold magenta] [grey]({scene_info['location_id']})[/grey]")
            rprint(f"{scene_info['description']}")
            if scene_info['exits']:
                rprint(f"[bold white]Exits:[/bold white] " + ", ".join(scene_info['exits']))
            last_look_result = scene_info
    except Exception as e:
        # Ignore if table empty or on error
        pass
    while True:
        cmd = input(">> ").strip()
        if cmd == "exit":
            break
        elif cmd.startswith("add_lore"):
            lore = cmd[len("add_lore"):].strip() or input("Paste lore to add: ")
            add_lore(lore)
            rprint("[green]Lore added.")
        elif cmd.startswith("generate_lore"):
            topic = cmd[len("generate_lore"):].strip() or input("Topic or query: ")
            new_lore = generate_lore(topic)
            rprint("[yellow]\nGenerated Lore:\n")
            rprint(new_lore)
            last_generated_lore = new_lore
        elif cmd.startswith("store_generated_lore"):
            if not last_generated_lore:
                rprint("[red]No generated lore to store. Use 'generate_lore' first.")
                continue
            store_generated_lore(last_generated_lore)
            rprint("[green]Generated lore stored.")
            last_generated_lore = ""
        elif cmd.startswith("chat_as "):
            rest = cmd[len("chat_as"):].strip()
            parts = rest.split(" ", 1)
            if len(parts) < 2:
                rprint("[red]Usage: chat_as <character_name> <user_message>")
                continue
            character_name = parts[0].strip()
            user_message = parts[1].strip()
            if not character_name or not user_message:
                rprint("[red]Usage: chat_as <character_name> <user_message>")
                continue
            try:
                reply = chat_as_character(character_name, user_message, limit=20)
            except KeyError as e:
                rprint(f"[red]Config error: {str(e)}")
                continue
            except Exception as e:
                rprint(f"[red]Error during LLM chat: {str(e)}")
                continue
            rprint("[magenta]\n" + reply)
        elif cmd == "/look":
            character_name = input("Character/session for /look: ").strip()
            if not character_name:
                rprint("[red]You must enter a character/session name.")
                continue
            try:
                scene_info = look(character_name)
                rprint(f"[bold magenta]{scene_info['display_name']}[/bold magenta] [grey]({scene_info['location_id']})[/grey]")
                rprint(f"{scene_info['description']}")
                if scene_info['exits']:
                    rprint(f"[bold white]Exits:[/bold white] " + ", ".join(scene_info['exits']))
                last_look_result = scene_info
            except Exception as e:
                # [fix 3] Show the traceback for easier debugging if an exception occurs in /look
                rprint(f"[red]Error in look: {str(e)}")
                rprint("[red]Traceback:")
                rprint(traceback.format_exc())
        elif cmd == "/save_look":
            character_name = input("Character/session for /save_look: ").strip()
            if not character_name:
                rprint("[red]You must enter a character/session name.")
                continue
            res = save_look(character_name)
            if res:
                rprint("[green]Look result saved as canonical lore for this location.")
            else:
                rprint("[red]Nothing to save. Use /look first, or see error.")
        elif cmd.startswith("/reset "):
            char_name = cmd[len("/reset "):].strip()
            session_id = chat_history.get_or_create_session(char_name)
            chat_history.reset_history(session_id)
            rprint(f"[blue]History for character '{char_name}' reset.")
        elif cmd.startswith("/history "):
            char_name = cmd[len("/history "):].strip()
            session_id = chat_history.get_or_create_session(char_name)
            hist = chat_history.get_history(session_id, limit=40)
            if not hist:
                rprint(f"[grey]No history for '{char_name}'.")
            else:
                for i, (role, msg) in enumerate(hist, 1):
                    who = "[bold yellow]You[/bold yellow]" if role == 'user' else f"[bold magenta]{char_name}[/bold magenta]"
                    rprint(f"{who}: {msg}")
        else:
            rprint("[red]Unknown command.")

if __name__ == "__main__":
    chat_loop()
