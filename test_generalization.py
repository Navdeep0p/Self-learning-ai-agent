from agent.executor import run_code_in_sandbox
from agent.llm import generate_code_solution
from agent.memory import EpisodicMemory
from agent.reflector import reflect_and_repair
from agent.validator import repair_syntax, validate_syntax

memory = EpisodicMemory()

UNSEEN_GENERALIZATION_TASK = {
    "id": "unseen_task_social_formatter",
    "task": (
        "Write a function `format_social_post(content: str, max_width: int, suffix: str = '...') -> str` that formats a post to fit within max_width characters.\n"
        "Rules:\n"
        "1. If len(content) <= max_width, return content unchanged.\n"
        "2. If len(suffix) > max_width, return ''.\n"
        "3. Otherwise, split content into words by spaces. Build the longest possible prefix of words joined by single spaces such that: len(prefix) + len(suffix) <= max_width.\n"
        "4. If at least one word fits, return f'{prefix}{suffix}'. If not even the first word can fit with the suffix, return ''.\n"
        "Include function definition and imports only."
    ),
    "test_harness": """
# Test 1: Fits within limit
assert format_social_post("Hello world", 20) == "Hello world", "Failed: Content under limit should remain unchanged"

# Test 2: Standard truncation with default suffix '...'
# Words: ["Breaking" (8), "news" (4), "from" (4), "the" (3)]
# "Breaking news from" is 18 chars. 18 + 3 = 21 <= 22. Next word "the" -> 22 + 3 = 25 > 22.
assert format_social_post("Breaking news from the city center", 22) == "Breaking news from...", f"Failed Test 2. Got: {repr(format_social_post('Breaking news from the city center', 22))}"

# Test 3: Custom suffix with distinct length
# "Alpha" = 5. 5 + 7 (" [more]") = 12 <= 18.
# "Alpha Beta" = 10. 10 + 7 = 17 <= 18.
# "Alpha Beta Gamma" = 16. 16 + 7 = 23 > 18.
assert format_social_post("Alpha Beta Gamma Delta", 18, suffix=" [more]") == "Alpha Beta [more]", f"Failed Test 3. Got: {repr(format_social_post('Alpha Beta Gamma Delta', 18, suffix=' [more]'))}"

# Test 4: max_width smaller than suffix
assert format_social_post("Any text here", 2, suffix="...") == "", "Failed: Should return '' if max_width < len(suffix)"

# Test 5: Exact boundary match
assert format_social_post("Exact fit", 9) == "Exact fit", "Failed: Exact fit should not append suffix"

print("ALL GENERALIZATION TESTS PASSED")
"""
}


def test_cross_task_transfer(max_attempts: int = 3):
    task_desc = UNSEEN_GENERALIZATION_TASK["task"]
    test_harness = UNSEEN_GENERALIZATION_TASK["test_harness"]

    print("=" * 70)
    print(f"GENERALIZATION TEST: {UNSEEN_GENERALIZATION_TASK['id']}")
    print("=" * 70)

    # 1. Semantic Vector Retrieval
    print("[1] Querying vector episodic memory for relevant past invariants...")
    past_lessons = memory.retrieve_relevant_lessons(task_desc, threshold=0.68)

    if past_lessons:
        print(f"[+] Retrieved {len(past_lessons)} transferable rule(s):")
        for idx, rule in enumerate(past_lessons, 1):
            print(f"    {idx}. {rule}")
    else:
        print("[-] Warning: No relevant lessons retrieved from memory store.")

    # 2. Initial Generation
    print("\n[Attempt 1] Generating candidate solution...")
    candidate_code = generate_code_solution(task_desc, past_lessons=past_lessons)

    is_valid, error_msg = validate_syntax(candidate_code)
    if not is_valid:
        print("  [AST Guard] Patching syntax error before sandbox execution...")
        candidate_code = repair_syntax(candidate_code, error_msg)

    last_diagnosis = ""
    for attempt in range(1, max_attempts + 1):
        print(f"--- RUN {attempt}/{max_attempts} ---")
        full_executable = candidate_code + "\n\n" + test_harness
        passed, output = run_code_in_sandbox(full_executable)

        if passed:
            print(f"[+] PASSED on attempt {attempt}!")
            if attempt == 1:
                print(">>> ZERO-SHOT TRANSFER VERIFIED ON ATTEMPT 1! <<<")
            else:
                print(">>> RECOVERED VIA REFLEXION! Updating consolidated memory... <<<")
                memory.save_lesson(
                    task=task_desc,
                    mistake=last_diagnosis,
                    lesson=last_diagnosis,
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

            is_valid, error_msg = validate_syntax(candidate_code)
            if not is_valid:
                candidate_code = repair_syntax(candidate_code, error_msg)

            print(f"[Diagnosis]: {last_diagnosis}")

    return False


if __name__ == "__main__":
    test_cross_task_transfer()