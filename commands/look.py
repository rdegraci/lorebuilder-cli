"""
commands/look.py

Handles the /look CLI command for LoreBuilder after refactoring.
"""
from locations import look
from rich import print as rprint

def handle(args, context):
    """
    Handles the /look CLI command.
    
    Args:
        args (list): Command arguments
        context (dict): Shared context dictionary
    """
    # If args are provided, use the first as character name, otherwise prompt
    if args:
        character_name = args[0]
    else:
        character_name = input("Character/session for /look: ").strip()
        
    if not character_name:
        rprint("[red]You must enter a character/session name.")
        return
    
    try:
        scene_info = look(character_name)
        rprint(f"[bold magenta]{scene_info['display_name']}[/bold magenta] [grey]({scene_info['location_id']})[/grey]")
        rprint(scene_info["description"])
        
        if scene_info['exits']:
            rprint(f"[bold white]Exits:[/bold white] " + ", ".join(scene_info["exits"]))
            
        if "_explanation" in scene_info and scene_info["_explanation"]:
            rprint(f"[dim][Reason:] {scene_info['_explanation']}[/dim]")
            
        context['last_look_result'] = scene_info
    except Exception as e:
        rprint(f"[red]Error in look: {str(e)}")