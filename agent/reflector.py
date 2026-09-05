import re
from agent.llm import call_llm, extract_code_block


def reflect_and_repair(task: str, failed_code: str, error_log: str) -> tuple[str, str]:
    """
    Analyzes execution traceback, isolates root causes, and returns
    a diagnosis along with an updated Python script.
    """
    prompt = f"""You are an expert Python software debugger.

TASK:
{task}

FAILED CODE ATTEMPT:
```python
{failed_code}
```

ERROR LOG / TRACEBACK:
{error_log}

INSTRUCTIONS:
1. Identify why the code failed in 1-2 concise sentences.
2. Provide the corrected, complete, and self-contained Python code.
3. Ensure all unit tests/asserts are present and the code prints "ALL TESTS PASSED" when successful.
4. Structure your response strictly as:
DIAGNOSIS: <brief explanation of the failure>
```python
<complete corrected code>
```
"""
    raw_response = call_llm(prompt)

    diag_match = re.search(r"DIAGNOSIS:\s*(.*?)(?=```|$)", raw_response, re.DOTALL)
    diagnosis = (
        diag_match.group(1).strip()
        if diag_match
        else "Corrected logical bug or edge case handling."
    )

    repaired_code = extract_code_block(raw_response)

    return diagnosis, repaired_code
