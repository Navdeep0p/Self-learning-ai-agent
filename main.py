from agent.executor import run_code_in_sandbox
from agent.llm import generate_code_solution
from agent.reflector import reflect_and_repair


def run_reflexion_pipeline(task: str, max_attempts: int = 3):
    print("=" * 70)
    print("PHASE 2: REFLEXION CYCLE (SELF-CORRECTION LOOP)")
    print(f"TASK: {task}")
    print("=" * 70)

    # 1. Initial Generation
    print("\n[Attempt 1/3] Generating initial solution...")
    current_code = generate_code_solution(task)

    for attempt in range(1, max_attempts + 1):
        print(f"\n--- TRIAL RUN {attempt}/{max_attempts} ---")
        passed, output = run_code_in_sandbox(current_code)

        if passed:
            print(f"\n[+] SUCCESS: Problem resolved on attempt {attempt}!")
            print(f"[+] Stdout:\n{output}")
            return {
                "success": True,
                "attempts_used": attempt,
                "final_code": current_code,
            }

        print(f"[-] FAILED on attempt {attempt}.")
        print(f"[-] Error Traceback:\n{output}")

        if attempt < max_attempts:
            print(f"\n[Reflector] Analyzing error log and generating fix...")
            diagnosis, current_code = reflect_and_repair(
                task=task,
                failed_code=current_code,
                error_log=output
            )
            print(f"[Diagnosis]: {diagnosis}")
        else:
            print(f"\n[!] Maximum attempts ({max_attempts}) exhausted without passing tests.")

    return {
        "success": False,
        "attempts_used": max_attempts,
        "final_code": current_code,
    }


if __name__ == "__main__":
    test_task = (
        "Write a function `run_length_encode(text: str) -> str` that performs "
        "basic run-length compression (e.g., 'aaabbc' -> 'a3b2c1'). "
        "Edge cases to handle with asserts:\n"
        "1. Empty string should return empty string ''.\n"
        "2. Single characters (e.g., 'a' -> 'a1').\n"
        "3. Case sensitivity matters ('aA' -> 'a1A1').\n"
        "Include comprehensive assert statements checking each rule and print 'ALL TESTS PASSED'."
    )
    run_reflexion_pipeline(test_task, max_attempts=3)
