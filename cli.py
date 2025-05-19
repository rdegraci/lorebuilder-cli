
"""
cli.py

Interactive command-line interface for LoreBuilder.
Handles input parsing, command dispatch, and user context.

Requires app initialization/config prior to calling start_cli().
"""
from rich import print as rprint
import traceback
from commands import COMMANDS_REGISTRY
import locations
from help import print_banner, print_command_menu, print_command_help


def start_cli(context):
    """
    Start the interactive CLI loop.

    Args:
        context (dict): Shared state and module references needed for command handlers.
    """
    print_banner()
    print_command_menu()
    
    # At script start: show last location for last-used character (if any)
    try:
        # Attempt to discover last character/session
        conn = locations.get_db_connection()
        c = conn.cursor()
        c.execute("SELECT character_name FROM character_location ORDER BY timestamp DESC LIMIT 1")
        row = c.fetchone()
        conn.close()
        if row:
            first_char = row[0]
            scene_info = locations.look(first_char)
            rprint(f"[bold green]Restored location for '{first_char}':")
            rprint(f"[bold magenta]{scene_info['display_name']}[/bold magenta] [grey]({scene_info['location_id']})[/grey]")
            rprint(f"{scene_info['description']}")
            if scene_info['exits']:
                rprint(f"[bold white]Exits:[/bold white] " + ", ".join(scene_info['exits']))
            if "_explanation" in scene_info and scene_info["_explanation"]:
                rprint(f"[dim][Reason:] {scene_info['_explanation']}[/dim]")
            context['last_look_result'] = scene_info
    except Exception as e:
        # Ignore if table empty or on error
        rprint(f"[dim]Note: {str(e)}[/dim]")
    
    rprint("[cyan]Ready! Enter commands below:[/cyan]")
    
    while True:
        try:
            cmd = input(">> ").strip()
            if cmd == "exit":
                break

            tokens = cmd.split()
            if not tokens:
                continue

            command = tokens[0]
            args = tokens[1:] if len(tokens) > 1 else []

            # Handle commands with or without leading slash
            canonical_command = command.lstrip('/')

            # Help command support
            if canonical_command == "help":
                if not args:
                    print_command_menu()
                else:
                    cmd_to_help = args[0]
                    handler = COMMANDS_REGISTRY.get(cmd_to_help)
                    if handler:
                        print_command_help(cmd_to_help, handler)
                    else:
                        rprint(f"[red]No help found: unknown command '{cmd_to_help}'.")
                continue

            # Find the handler in the registry
            handler = COMMANDS_REGISTRY.get(canonical_command)

            if handler:
                handler(args, context)
            else:
                rprint(f"[red]Unknown command: {command}. Type a command from the list above.")
        except Exception as e:
            traceback.print_exc()
            rprint(f"[red]Error processing command: {str(e)}")


