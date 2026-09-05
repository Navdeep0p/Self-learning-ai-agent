import ast
import re
from agent.llm import call_llm, extract_code_block

BACKTICKS = chr(96) * 3


def validate_syntax(code: str) -> tuple[bool, str]:
    """
    Parses code into an AST.
    Returns (True, "") if valid, or (False, error_details) on SyntaxError.
    """
    try:
        ast.parse(code)
        return True, ""
    except SyntaxError as e:
        error_msg = f"SyntaxError at line {e.lineno}, column {e.offset}: {e.msg}\n--> {e.text}"
        return False, error_msg.strip()


def repair_syntax(code: str, error_details: str, max_syntax_retries: int = 2) -> str:
    """
    Fast zero-execution retry loop targeting only syntax errors (e.g. unclosed parentheses).
    Does not consume a sandbox execution attempt.
    """
    current_code = code

    for attempt in range(1, max_syntax_retries + 1):
        is_valid, error_msg = validate_syntax(current_code)
        if is_valid:
            return current_code

        print(f"  [AST Guard] Detected syntax error before execution (Attempt {attempt}/{max_syntax_retries}):")
        print(f"  {error_msg.splitlines()[0]}")

        prompt = f"""You are a Python syntax repair specialist.
The following Python script failed AST parsing with a syntax error.

CODE:
{BACKTICKS}python
{current_code}
{BACKTICKS}

PARSER ERROR:
{error_msg}

INSTRUCTIONS:
1. Fix ONLY the syntax error (e.g., balance parentheses, fix quotation marks, resolve indentation).
2. Maintain the exact same logic.
3. Return ONLY valid executable Python in a {BACKTICKS}python code block.
"""
        raw_response = call_llm(prompt)
        repaired = extract_code_block(raw_response)

        # Strip any extraneous line numbering artifacts
        clean_lines = [re.sub(r"^\s*\d+\s*\|\s*", "", line) for line in repaired.split("\n")]
        current_code = "\n".join(clean_lines)

    return current_code