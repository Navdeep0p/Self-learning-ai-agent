import argparse
import sys
import time
from rich.prompt import Prompt

from agent.benchmark import BENCHMARK_TASKS
from agent.executor import run_code_in_sandbox
from agent.llm import generate_code_solution
from agent.memory import EpisodicMemory
from agent.reflector import reflect_and_repair
from agent.ui import (
    console,
    render_ast_warning,
    render_attempt_header,
    render_code_diff,
    render_code_solution,
    render_diagnosis,
    render_failure,
    render_memory_injection,
    render_success,
    render_task_header,
)
from agent.validator import repair_syntax, validate_syntax

memory = EpisodicMemory()


def run_learning_agent(task_data: dict, max_attempts: int = 3) -> bool:
    task_desc = task_data["task"]
    test_harness = task_data["test_harness"]
    task_id = task_data.get("id", "custom_task")

    render_task_header(task_id)

    # 1. Vector Retrieval
    with console.status("[bold magenta]Searching vector episodic memory...", spinner="dots"):
        past_lessons = memory.retrieve_relevant_lessons(task_desc)

    render_memory_injection(past_lessons)

    # 2. Initial Generation
    render_attempt_header(1, max_attempts)
    with console.status("[bold green]Synthesizing candidate function (qwen2.5-coder:7b)...", spinner="aesthetic"):
        candidate_code = generate_code_solution(task_desc, past_lessons=past_lessons)

    # 3. AST Guard Pre-Validation
    is_valid, error_msg = validate_syntax(candidate_code)
    if not is_valid:
        render_ast_warning(error_msg)
        with console.status("[bold yellow]AST Guard repairing syntax...", spinner="dots"):
            candidate_code = repair_syntax(candidate_code, error_msg)

    render_code_solution(candidate_code, title="Initial Candidate")

    last_diagnosis = ""
    for attempt in range(1, max_attempts + 1):
        if attempt > 1:
            render_attempt_header(attempt, max_attempts)

        # Execution in sandbox
        with console.status(f"[bold cyan]Running verification sandbox (Attempt {attempt})...", spinner="dots"):
            full_executable = candidate_code + "\n\n" + test_harness
            passed, output = run_code_in_sandbox(full_executable)

        if passed:
            render_success(attempt)
            if attempt > 1 and last_diagnosis:
                memory.save_lesson(
                    task=task_desc,
                    mistake=last_diagnosis,
                    lesson=last_diagnosis,
                )
            return True

        # Failure handling
        render_failure(output.strip())

        if attempt < max_attempts:
            failing_code = candidate_code
            with console.status("[bold yellow]Reflector diagnosing traceback and synthesizing repair...", spinner="bouncingBar"):
                last_diagnosis, candidate_code = reflect_and_repair(
                    task=task_desc,
                    failed_code=failing_code,
                    error_log=output,
                )

            # Validate repaired syntax
            is_valid, error_msg = validate_syntax(candidate_code)
            if not is_valid:
                render_ast_warning(error_msg)
                with console.status("[bold yellow]AST Guard repairing patch syntax...", spinner="dots"):
                    candidate_code = repair_syntax(candidate_code, error_msg)

            render_diagnosis(last_diagnosis)
            render_code_diff(failing_code, candidate_code)

    return False


def interactive_mode():
    console.rule("[bold cyan]SELF-LEARNING AGENT: INTERACTIVE REPL[/bold cyan]", style="cyan")
    console.print("[dim]Enter multi-line input. Submit with an empty line or Ctrl+D.[/dim]\n")

    console.print("[bold yellow]1. Function / Task Specification:[/bold yellow]")
    lines = []
    while True:
        try:
            line = input()
            if not line and lines:
                break
            lines.append(line)
        except EOFError:
            break

    task_prompt = "\n".join(lines).strip()
    if not task_prompt:
        console.print("[red]Task prompt cannot be empty.[/red]")
        sys.exit(0)

    console.print("\n[bold yellow]2. Test Harness / Assertions:[/bold yellow]")
    harness_lines = []
    while True:
        try:
            line = input()
            if not line and harness_lines:
                break
            harness_lines.append(line)
        except EOFError:
            break

    test_harness = "\n".join(harness_lines).strip()
    if not test_harness:
        console.print("[red]Test harness cannot be empty.[/red]")
        sys.exit(0)

    task_payload = {
        "id": "interactive_session",
        "task": task_prompt,
        "test_harness": test_harness,
    }
    run_learning_agent(task_payload)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Autonomous Self-Learning Coding Agent")
    parser.add_argument("--interactive", "-i", action="store_true", help="Launch interactive REPL mode")
    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
    else:
        for task in BENCHMARK_TASKS:
            run_learning_agent(task)
            time.sleep(2)