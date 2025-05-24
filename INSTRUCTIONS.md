# LoreBuilder CLI Usage Instructions

Welcome to LoreBuilder CLI! This guide provides a practical workflow and command examples for building a consistent fictional world and exploring its characters, lore, and interactions.

---

## 1. Start the Application

```bash
python app.py
```
This launches the interactive command-line interface.

---

## 2. Add Initial Lore
Begin by adding world background or foundational facts. This creates context for the world and its inhabitants.

```bash
add_lore The city of Ardelune is ruled by a council of scholars and hidden mages.
add_lore The Crystal Lake glows at midnight and is rumored to be haunted.
add_lore All travel between villages is watched by the mysterious Order of Shadows.
```

---

## 3. List and Query Lore
Retrieve all lore for review, or search for specific themes and facts:

```bash
list_all_lore
query_lore council
query_lore Crystal Lake
```

---

## 4. Generate New Lore
Use natural language prompts to ask the LLM to author new details, always integrating existing context:

```bash
generate_lore Describe a festival held by the people of Ardelune.
generate_lore What secrets are rumored about the Order of Shadows?
```

The last generated lore is kept in memory for easy saving.

---

## 5. Store Generated Lore
When satisfied with generated lore, store it permanently:

```bash
store_generated_lore
```

---

## 6. Extract and Explore Characters
The system can extract character names from all saved lore. List all detected characters:

```bash
list_characters
```

Add more lore about characters or create new individuals via `add_lore` or LLM generation.

---

## 7. Chat As Characters
Begin an in-character conversation session using any extracted or manually-remembered character name:

```bash
chat_as Mara
chat_as The Mage of the Lake
```

Converse as the character or with the character, with all past dialogue remembered per character and session.

---

## 8. Deleting and Resetting
Remove incorrect or obsolete lore with:

```bash
delete_lore <lore_id>
```

List all lore to view lore_id values beforehand. Reset or export chat history using relevant commands if available.

---

## 9. Help and Command Reference
See a summary of all available commands at any time:

```bash
help
```
Or for details on a specific command:
```bash
help add_lore
```

---

## Tips for World Consistency
- When adding or generating lore, reference previous details to avoid contradictions.
- Use `query_lore` to double-check facts and ensure narrative cohesion.
- Keep your "Order of Shadows" or other recurring entities consistent in lore and chat.
- Regularly store generated lore to avoid accidental loss.
- Use unique names and explicit relationships to help the entity extractor work effectively.

---

Enjoy world-building with LoreBuilder CLI! For issues or more advanced guidance, see the README and ARCHITECTURE.md, or contact project maintainers via GitHub Issues or email.
