import yaml
import chromadb
from chromadb.utils import embedding_functions
import litellm
from rich import print as rprint
from datetime import datetime
import os
from dotenv import load_dotenv

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

# --- Init LLM (with LiteLLM) ---
def call_llm(prompt):
    response = litellm.completion(
        model=config["llm_provider"], api_key=llm_api_key, messages=[{"role": "system", "content": prompt}]
    )
    return response['choices'][0]['message']['content']

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
    return call_llm(prompt)

def store_generated_lore(text, metadata=None):
    add_lore(text, metadata)

# --- CLI Loop ---
def chat_loop():
    rprint("[bold cyan]LoreBuilder CLI - Commands: add_lore, generate_lore, store_generated_lore, exit")
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
        else:
            rprint("[red]Unknown command.")

if __name__ == "__main__":
    chat_loop()
