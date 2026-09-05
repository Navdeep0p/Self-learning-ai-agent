import subprocess
import sys


def run_code_in_sandbox(code: str, timeout: int = 5) -> tuple[bool, str]:
    """
    Executes a Python code string in a fresh, isolated subprocess.
    Returns:
        (success: bool, output: str)
    """
    try:
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, f"TimeoutError: Execution exceeded {timeout} seconds limit (infinite loop prevention)."
    except Exception as exc:
        return False, f"ExecutionError: {str(exc)}"