import yaml
import chromadb
from chromadb.utils import embedding_functions
import litellm
from rich import print as rprint
from datetime import datetime
import os
from dotenv import load_dotenv
import chat_history

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
    rprint("[bold cyan]LoreBuilder CLI - Commands: add_lore, generate_lore, store_generated_lore, chat_as <character_name> <user_message>, /reset <character>, /history <character>, exit")
    last_generated_lore = ""
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
                    who = "[bold yellow]You" if role == 'user' else f"[bold magenta]{char_name}"
                    rprint(f"{who}:[/bold] {msg}")
        else:
            rprint("[red]Unknown command.")

if __name__ == "__main__":
    chat_loop()
