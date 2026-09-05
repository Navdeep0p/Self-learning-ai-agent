import difflib
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

console = Console()


def render_task_header(task_id: str):
    console.print()
    console.rule(f"[bold cyan]EVALUATING: {task_id}[/bold cyan]", style="cyan")


def render_memory_injection(rules: list[str]):
    if not rules:
        return

    table = Table(
        title="[bold magenta]🧠 Episodic Memory Injected[/bold magenta]",
        show_header=True,
        header_style="bold magenta",
        expand=True,
        border_style="magenta",
    )
    table.add_column("#", style="dim", width=4, justify="center")
    table.add_column("Distilled Invariant / Rule", style="white")

    for idx, rule in enumerate(rules, 1):
        table.add_row(str(idx), rule)

    console.print(table)


def render_ast_warning(msg: str):
    console.print(
        Panel(
            f"[bold yellow]AST Guard caught a pre-execution syntax issue:[/bold yellow]\n{msg}",
            title="[yellow]Pre-Validation Filter[/yellow]",
            border_style="yellow",
        )
    )


def render_attempt_header(attempt: int, max_attempts: int):
    console.print(f"\n[bold blue]━━━ TRIAL {attempt}/{max_attempts} ━━━[/bold blue]")


def render_code_solution(code: str, title: str = "Candidate Solution"):
    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title=f"[green]{title}[/green]", border_style="green"))


def render_failure(error_msg: str):
    console.print(
        Panel(
            Text(error_msg, style="bold red"),
            title="[bold red]✖ Execution / Test Failure[/bold red]",
            border_style="red",
        )
    )


def render_diagnosis(diagnosis: str):
    console.print(
        Panel(
            f"[bold yellow]Reflexion Diagnosis:[/bold yellow]\n{diagnosis}",
            title="[yellow]🔍 Root-Cause Analysis[/yellow]",
            border_style="yellow",
        )
    )


def render_code_diff(old_code: str, new_code: str):
    """Renders a colorized unified diff between failing code and repaired code."""
    old_lines = old_code.splitlines(keepends=True)
    new_lines = new_code.splitlines(keepends=True)
    diff = list(difflib.unified_diff(old_lines, new_lines, fromfile="Failed", tofile="Repaired", n=2))

    if not diff:
        return

    diff_text = Text()
    for line in diff:
        if line.startswith("+") and not line.startswith("+++"):
            diff_text.append(line, style="bold green")
        elif line.startswith("-") and not line.startswith("---"):
            diff_text.append(line, style="bold red")
        elif line.startswith("@"):
            diff_text.append(line, style="cyan")
        else:
            diff_text.append(line, style="dim")

    console.print(
        Panel(
            diff_text,
            title="[bold cyan]📝 Reflector Patch (Diff)[/bold cyan]",
            border_style="cyan",
        )
    )


def render_success(attempt: int):
    console.print(
        Panel(
            f"[bold green]✔ PASSED ON ATTEMPT {attempt}[/bold green]",
            border_style="green",
        )
    )


def render_synthesized_tests(test_code: str):
    syntax = Syntax(test_code, "python", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title="[magenta]🧪 Synthesized Verification Suite[/magenta]", border_style="magenta"))