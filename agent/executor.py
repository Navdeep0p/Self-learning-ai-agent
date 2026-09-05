import subprocess
import sys


def run_code_in_sandbox(code: str, timeout_seconds: int = 15) -> tuple[bool, str]:
    """
    Executes code in an isolated Python subprocess.
    Returns (True, stdout) on success, or (False, stderr/stdout) on failure.
    """
    try:
        proc = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )

        if proc.returncode == 0:
            return True, proc.stdout
        else:
            # Capture both stderr and stdout in case assertions print extra info
            error_output = proc.stderr if proc.stderr else proc.stdout
            return False, error_output.strip()

    except subprocess.TimeoutExpired:
        return False, f"TimeoutError: Execution exceeded {timeout_seconds} seconds."
    except Exception as e:
        return False, f"ExecutionError: {str(e)}"