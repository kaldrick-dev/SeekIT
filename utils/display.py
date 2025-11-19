"""Small helper functions for printing friendly CLI messages."""

from typing import Iterable, Optional, Sequence, Tuple

def divider(char: str = "-", width: int = 50) -> str:
    """Return a line divider so menus look tidy."""
    line = char * max(10, width)
    print(line)
    return line


def print_heading(message: str) -> None:
    """Show a short section heading."""
    divider("=")
    print(message.upper())
    divider("=")


def print_info(message: str) -> None:
    """Display neutral information."""
    print(f"[INFO] {message}")


def print_success(message: str) -> None:
    """Display a success tick."""
    print(f"[✓] {message}")


def print_error(message: str) -> None:
    """Display a friendly error."""
    print(f"[!] {message}")


def print_warning(message: str) -> None:
    """Display a warning."""
    print(f"[?] {message}")


def ask_input(prompt: str, allow_empty: bool = False) -> str:
    """Ask the user for input and re-prompt when needed."""
    while True:
        response = input(f"{prompt.strip()} ").strip()
        if response or allow_empty:
            return response
        print_error("Please type something or press Ctrl+C to quit.")


def ask_int(prompt: str, allow_empty: bool = False) -> Optional[int]:
    """
    Ask the user for an integer value.

    The helper reuses ask_input so validation is centralized in one place.
    """
    while True:
        response = ask_input(prompt, allow_empty=allow_empty)
        if allow_empty and not response:
            return None
        try:
            return int(response)
        except ValueError:
            print_error("Please enter a whole number (e.g. 42). Try again.")


def print_menu(title: str, options: Iterable[Tuple[str, str]]) -> str:
    """
    Show a numbered menu and return the user's selection as a string.

    Args:
        title: Heading displayed above the menu.
        options: Iterable of (option_id, label) pairs.
    """
    print_heading(title)
    for option_id, label in options:
        print(f"{option_id}. {label}")
    divider()
    return ask_input("Choose an option:", allow_empty=False)


def print_table(headers: Sequence[str], rows: Iterable[Sequence[object]]) -> None:
    """
    Render a super lightweight table in the console.

    The helper keeps spacing readable without depending on any third-party libs.
    """
    header_cells = [str(header) for header in headers]
    rows_as_text = [
        tuple("" if cell is None else str(cell) for cell in row) for row in rows
    ]

    if not header_cells:
        raise ValueError("print_table requires at least one header.")

    column_count = len(header_cells)
    widths = [len(cell) for cell in header_cells]

    for row in rows_as_text:
        if len(row) != column_count:
            raise ValueError("Each row must match the header length.")
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(cell))

    row_template = " | ".join(f"{{:<{width}}}" for width in widths)

    divider()
    print(row_template.format(*header_cells))
    divider()
    for row in rows_as_text:
        print(row_template.format(*row))
    divider()
