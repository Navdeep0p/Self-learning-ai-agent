import time
from agent.benchmark import BENCHMARK_TASKS
from agent.executor import run_code_in_sandbox
from agent.llm import generate_code_solution
from agent.memory import EpisodicMemory
from agent.reflector import reflect_and_repair
from agent.validator import repair_syntax, validate_syntax

memory = EpisodicMemory()


def run_learning_agent(task_data: dict, max_attempts: int = 3):
    task_desc = task_data["task"]
    test_harness = task_data["test_harness"]

    print("\n" + "=" * 70)
    print(f"EVALUATING: {task_data['id']}")
    print("=" * 70)

    # 1. Retrieve episodic memory via dense vector cosine similarity
    past_lessons = memory.retrieve_relevant_lessons(task_desc)
    if past_lessons:
        print(f"[Memory] Injected {len(past_lessons)} stored rule(s):")
        for idx, rule in enumerate(past_lessons, 1):
            print(f"  {idx}. {rule}")

    # 2. Initial generation
    print("\n[Attempt 1] Generating function...")
    candidate_code = generate_code_solution(task_desc, past_lessons=past_lessons)

    # AST Guard: pre-validate syntax prior to first sandbox execution
    is_valid, error_msg = validate_syntax(candidate_code)
    if not is_valid:
        candidate_code = repair_syntax(candidate_code, error_msg)

    last_diagnosis = ""
    for attempt in range(1, max_attempts + 1):
        print(f"--- RUN {attempt}/{max_attempts} ---")

        # Combine candidate code with evaluation harness
        full_executable = candidate_code + "\n\n" + test_harness
        passed, output = run_code_in_sandbox(full_executable)

        if passed:
            print(f"[+] PASSED on attempt {attempt}!")
            if attempt > 1 and last_diagnosis:
                memory.save_lesson(
                 task=task_desc,
                 mistake=last_diagnosis,
                 lesson=last_diagnosis,  # Pure, reusable invariant
                )
            return True

        print(f"[-] FAILED on attempt {attempt}.")
        print(f"[-] Error: {output.strip()}")

        if attempt < max_attempts:
            print("[Reflector] Repairing code against failed assertion...")
            last_diagnosis, candidate_code = reflect_and_repair(
                task=task_desc,
                failed_code=candidate_code,
                error_log=output,
            )

            # AST Guard: ensure reflector's patch is syntactically valid before sandbox run
            is_valid, error_msg = validate_syntax(candidate_code)
            if not is_valid:
                candidate_code = repair_syntax(candidate_code, error_msg)

            print(f"[Diagnosis]: {last_diagnosis}")

    return False


if __name__ == "__main__":
    for task in BENCHMARK_TASKS:
        run_learning_agent(task)
        time.sleep(3)  # Thermal pacing interval