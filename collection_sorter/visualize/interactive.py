from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from rich.prompt import Prompt, Confirm

from collection_sorter.common.exceptions import UserInterruptError
from collection_sorter.logging import console


def confirm_action(
    message: str, 
    default: bool = False
) -> bool:
    """
    Ask for confirmation before performing an action.
    
    Args:
        message: The message to display
        default: Default response (True for yes, False for no)
        
    Returns:
        True if confirmed, False otherwise
        
    Raises:
        UserInterruptError: If user cancels with Ctrl+C
    """
    try:
        return Confirm.ask(message, default=default, console=console)
    except KeyboardInterrupt:
        raise UserInterruptError()

def prompt_input(
    message: str,
    default: Optional[str] = None,
    choices: Optional[List[str]] = None,
    password: bool = False
) -> str:
    """
    Prompt for user input.
    
    Args:
        message: The message to display
        default: Default value if user presses Enter
        choices: List of valid choices
        password: Whether to hide input (for passwords)
        
    Returns:
        User input
        
    Raises:
        UserInterruptError: If user cancels with Ctrl+C
    """
    try:
        return Prompt.ask(
            message,
            default=default,
            choices=choices,
            password=password,
            console=console
        )
    except KeyboardInterrupt:
        raise UserInterruptError()

def select_destination(
    source_path: Union[str, Path],
    default_destination: Optional[Union[str, Path]] = None
) -> str:
    """
    Prompt user to select a destination for files.
    
    Args:
        source_path: Source path
        default_destination: Default destination path
        
    Returns:
        Selected destination path
        
    Raises:
        UserInterruptError: If user cancels with Ctrl+C
    """
    src_path = Path(source_path)
    default = str(default_destination) if default_destination else str(src_path.parent / "processed")
    
    console.print(f"[bold]Source:[/bold] {src_path}")
    destination = prompt_input(
        "Enter destination path",
        default=default
    )
    
    # Create destination if it doesn't exist
    dest_path = Path(destination)
    if not dest_path.exists():
        if confirm_action(f"Destination {dest_path} does not exist. Create it?", default=True):
            dest_path.mkdir(parents=True, exist_ok=True)
    
    return str(dest_path)

def interactive_preview(
    source_path: Union[str, Path],
    changes: Dict[str, str],
    operation: str = "rename"
) -> Dict[str, str]:
    """
    Show an interactive preview of changes and allow user to modify them.
    
    Args:
        source_path: Source path
        changes: Dictionary of changes (original -> new)
        operation: Type of operation (rename, move, etc.)
        
    Returns:
        Dictionary of confirmed changes
        
    Raises:
        UserInterruptError: If user cancels with Ctrl+C
    """
    console.print(f"\n[bold]Preview of {operation} operations for {source_path}[/bold]")
    console.print("-" * 80)
    
    for original, new in changes.items():
        console.print(f"[yellow]{original}[/yellow] -> [green]{new}[/green]")
    
    console.print("-" * 80)
    
    if not confirm_action(
        f"Proceed with {len(changes)} {operation} operations?", 
        default=True
    ):
        return {}
    
    return changes

def show_results(
    results: Dict[str, Any],
    operation: str = "Process"
) -> None:
    """
    Show results of an operation.
    
    Args:
        results: Dictionary of results
        operation: Type of operation
    """
    console.print(f"\n[bold]{operation} Results[/bold]")
    console.print("-" * 80)
    
    success_count = 0
    error_count = 0
    
    for source, result in results.items():
        if result.get("success", False):
            success_count += 1
            console.print(f"[green]✓[/green] {source}: Success")
        else:
            error_count += 1
            error = result.get("error", "Unknown error")
            console.print(f"[red]✗[/red] {source}: {error}")
    
    console.print("-" * 80)
    console.print(f"Total: {len(results)}, Success: {success_count}, Errors: {error_count}")
    console.print("")