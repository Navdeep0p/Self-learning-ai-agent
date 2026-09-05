import re
from agent.llm import call_llm, extract_code_block

BACKTICKS = chr(96) * 3


def format_code_with_lines(code: str) -> str:
    lines = code.strip().split("\n")
    return "\n".join(f"{idx + 1:02d} | {line}" for idx, line in enumerate(lines))


def reflect_and_repair(task: str, failed_code: str, error_log: str) -> tuple[str, str]:
    """
    Analyzes execution traceback, distills a general rule for long-term memory,
    and returns the repaired script.
    """
    annotated_code = format_code_with_lines(failed_code)

    prompt = f"""You are an expert Python software debugger.

TASK:
{task}

FAILED CODE (WITH LINE NUMBERS):
{BACKTICKS}python
{annotated_code}
{BACKTICKS}

TEST HARNESS ERROR LOG:
{error_log}

INSTRUCTIONS:
1. Write "RULE: " followed by a single, generalized, forward-looking programming rule that prevents this mistake in the future. (Do NOT mention line numbers or test cases; write an actionable coding invariant).
2. Provide the complete corrected Python function implementation inside a {BACKTICKS}python code block.
3. Do NOT include assert statements or markdown fences within the code.
"""
    raw_response = call_llm(prompt)

    rule_match = re.search(r"RULE:\s*(.*?)(?=" + BACKTICKS + r"|$)", raw_response, re.DOTALL)
    rule = (
        rule_match.group(1).strip()
        if rule_match
        else "Ensure strict boundary validation and correct type handling."
    )
    # Remove conversational artifacts
    rule = rule.split("\n")[0].replace("`", "").strip()

    repaired_code = extract_code_block(raw_response)
    clean_lines = [
        re.sub(r"^\s*\d+\s*\|\s*", "", line)
        for line in repaired_code.split("\n")
    ]
    repaired_code = "\n".join(clean_lines)

    return rule, repaired_code