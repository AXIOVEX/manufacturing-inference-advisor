from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

ACTIONS = {
    "1": ("Setup/rebuild and connect Codex", "setup"),
    "2": ("Validate Docker MCP profile", "test"),
    "3": ("Call both MCP servers", "verify"),
    "4": ("Print gateway command", "command"),
}


def _script() -> Path:
    candidates = [Path.cwd() / "scripts" / "docker_mcp.py"]
    candidates.append(Path(__file__).resolve().parents[2] / "scripts" / "docker_mcp.py")
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("run the manager from the manufacturing-inference-advisor repository")


def run_action(action: str) -> int:
    return subprocess.run([sys.executable, str(_script()), action], check=False).returncode


def main() -> None:
    console = Console()
    while True:
        console.print(
            Panel(
                "One profile: Michigan workforce evidence + manufacturing inference planning",
                title="Manufacturing Intelligence · Docker MCP",
                border_style="cyan",
            )
        )
        table = Table(show_header=False, box=None)
        for key, (label, _) in ACTIONS.items():
            table.add_row(f"[cyan]{key}[/cyan]", label)
        table.add_row("[cyan]q[/cyan]", "Quit")
        console.print(table)
        choice = Prompt.ask("Action", choices=[*ACTIONS, "q"], default="3", console=console)
        if choice == "q":
            return
        label, action = ACTIONS[choice]
        console.print(f"[bold]{label}[/bold]")
        code = run_action(action)
        console.print("[green]Complete[/green]" if code == 0 else f"[red]Failed ({code})[/red]")


if __name__ == "__main__":
    main()
