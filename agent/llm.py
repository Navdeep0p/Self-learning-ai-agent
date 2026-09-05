import re
import sys
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "qwen2.5-coder:7b"


def call_llm(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """Sends a completion request to the local Ollama API."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_predict": 1024,
        },
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        response.raise_for_status()
        return response.json().get("response", "")
    except requests.exceptions.ConnectionError:
        print("\n[!] Connection Error: Unable to reach Ollama at http://localhost:11434.")
        print("    Ensure the Ollama service is active via `ollama serve`.")
        sys.exit(1)


def generate_code_solution(task: str, model: str = DEFAULT_MODEL) -> str:
    """Asks the LLM to write self-contained code with test assertions."""
    prompt = f"""You are an autonomous Python software engineer.

TASK:
{task}

REQUIREMENTS:
1. Write pure, self-contained Python 3 code that solves the problem.
2. Include assert statements (unit tests) at the bottom covering standard cases and edge cases.
3. If all assertions succeed, print "ALL TESTS PASSED".
4. Output ONLY valid executable code inside a single ```python ... ``` block. No markdown chatter outside the code block.
"""
    raw_response = call_llm(prompt, model=model)
    return extract_code_block(raw_response)


def extract_code_block(raw_text: str) -> str:
    """Extracts raw code from Markdown fences."""
    pattern = r"```(?:python)?\s*(.*?)\s*```"
    match = re.search(pattern, raw_text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else raw_text.strip()