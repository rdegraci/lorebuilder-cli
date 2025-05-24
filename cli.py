
"""
cli.py

Interactive command-line interface for LoreBuilder.
Handles input parsing, command dispatch, and user context.

Requires app initialization/config prior to calling start_cli().
"""
from rich import print as rprint
import traceback
from commands import COMMANDS_REGISTRY
from help import print_banner, print_command_menu, print_command_help
from cli_utils import cli_error, cli_warn, cli_info, cli_success  # centralized messaging


def start_cli(context, verbose=False):
    """
    Start the interactive CLI loop.

    Args:
        context (dict): Shared state and module references needed for command handlers.
        verbose (bool): Enable verbose output (prints tracebacks and debug if True).
    """
    print_banner()
    print_command_menu()
    
    cli_info("Ready! Enter commands below:")
    
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
                        cli_error(f"No help found: unknown command '{cmd_to_help}'.")
                continue

            # Find the handler in the registry
            handler = COMMANDS_REGISTRY.get(canonical_command)

            if handler:
                handler(args, context)
            else:
                cli_error(f"Unknown command: {command}. Type a command from the list above.")
        except Exception as e:
            if verbose:
                traceback.print_exc()
            cli_error(f"Error processing command: {str(e)}")


