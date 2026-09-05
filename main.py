from agent.executor import run_code_in_sandbox
from agent.llm import generate_code_solution


def run_phase1(task: str):
    print("=" * 70)
    print("PHASE 1: BASE REACT TRIAL")
    print(f"TASK: {task}")
    print("=" * 70)

    # 1. Generate code
    print("\n[Step 1] Querying local model for solution...")
    code = generate_code_solution(task)

    print("\n--- GENERATED PYTHON SCRIPT ---")
    print(code)
    print("-" * 31)

    # 2. Execute in isolated sandbox
    print("\n[Step 2] Executing in isolated subprocess sandbox...")
    passed, output = run_code_in_sandbox(code)

    # 3. Output result
    print("\n[Step 3] Verification Outcome:")
    if passed:
        print("[SUCCESS] All assertions passed!")
        print(f"Stdout:\n{output}")
    else:
        print("[FAILED] Code encountered an error or failed assertions.")
        print(f"Stderr / Diagnostics:\n{output}")

    return passed


if __name__ == "__main__":
    sample_task = (
        "Write a function `flatten(lst: list) -> list` that flattens arbitrary levels "
        "of nested lists into a single flat list of integers. "
        "Include assert statements for empty lists, single values, and mixed depths."
    )
    run_phase1(sample_task)