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
            "num_predict": 2048,
        },
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=90)
        response.raise_for_status()
        return response.json().get("response", "")
    except requests.exceptions.ConnectionError:
        print("\n[!] Connection Error: Unable to reach Ollama at http://localhost:11434.")
        print("    Ensure the Ollama service is active via `ollama serve`.")
        sys.exit(1)


def extract_code_block(raw_text: str) -> str:
    """Robustly extracts pure Python code from model responses."""
    matches = re.findall(r"```(?:python|py)?\s*\n(.*?)```", raw_text, re.DOTALL | re.IGNORECASE)
    if matches:
        return max(matches, key=len).strip()

    if "```" in raw_text:
        parts = raw_text.split("```")
        if len(parts) >= 2:
            code = parts[1]
            if code.lower().startswith("python"):
                code = code[6:]
            return code.strip()

    return raw_text.strip()


def generate_code_solution(task: str, past_lessons: list = None, model: str = DEFAULT_MODEL) -> str:
    """Prompts the LLM to write only the function solution."""
    lessons_section = ""
    if past_lessons:
        formatted = "\n".join(f"- {lesson}" for lesson in past_lessons)
        lessons_section = f"\n### CRITICAL LESSONS LEARNED:\n{formatted}\nAdhere strictly to these rules.\n"

    prompt = f"""You are an autonomous Python software engineer.

TASK:
{task}
{lessons_section}
REQUIREMENTS:
1. Write ONLY the complete Python 3 function implementation and necessary imports.
2. DO NOT include test assertions, example usage, or driver code at the bottom.
3. Output ONLY the code inside a single ```python code block.
"""
    raw_response = call_llm(prompt, model=model)
    return extract_code_block(raw_response)