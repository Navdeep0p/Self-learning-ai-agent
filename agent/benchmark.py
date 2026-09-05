BENCHMARK_TASKS = [
    {
        "id": "task_1_valid_parentheses",
        "task": (
            "Write a function `is_valid_brackets(s: str) -> bool` that verifies if brackets '()[]{}' are properly closed and nested.\n"
            "Include function definition and necessary imports."
        ),
        "test_harness": """
assert is_valid_brackets("()") is True, "Failed on '()'"
assert is_valid_brackets("()[]{}") is True, "Failed on '()[]{}'"
assert is_valid_brackets("(]") is False, "Failed on '(]'"
assert is_valid_brackets("([)]") is False, "Failed on '([)]'"
assert is_valid_brackets("{[]}") is True, "Failed on '{[]}'"
assert is_valid_brackets("") is True, "Failed on empty string"
assert is_valid_brackets("[") is False, "Failed on single bracket"
print("ALL TESTS PASSED")
"""
    },
    {
        "id": "task_2_longest_consecutive",
        "task": (
            "Write a function `longest_consecutive(nums: list[int]) -> int` that returns the length "
            "of the longest sequence of consecutive elements in an unsorted array.\n"
            "Include function definition and necessary imports."
        ),
        "test_harness": """
assert longest_consecutive([100, 4, 200, 1, 3, 2]) == 4, "Failed on standard array (expected 4 for [1,2,3,4])"
assert longest_consecutive([0, 3, 7, 2, 5, 8, 4, 6, 0, 1]) == 9, "Failed on array with duplicates"
assert longest_consecutive([]) == 0, "Failed on empty list"
assert longest_consecutive([7]) == 1, "Failed on single element"
assert longest_consecutive([9, 1, 4, 7, 3, -1, 0, 5, 8, -2, 6]) == 7, "Failed on negative numbers"
print("ALL TESTS PASSED")
"""
    },
    {
        "id": "task_3_truncate_words",
        "task": (
            "Write a function `truncate_text(text: str, max_chars: int) -> str` that truncates text to fit within max_chars without cutting words in half.\n"
            "If text fits within max_chars, return it as-is.\n"
            "If it must be truncated, cut at the last possible word boundary and append '...'. The total length including '...' must NOT exceed max_chars.\n"
            "If max_chars < 3, return ''."
        ),
        "test_harness": """
assert truncate_text("hello world", 15) == "hello world", "Failed on fitting text"
assert truncate_text("hello beautiful world", 15) == "hello...", "Failed on word-boundary truncation"
assert truncate_text("hello world", 2) == "", "Failed on max_chars < 3"
assert truncate_text("the quick brown fox", 10) == "the...", "Failed on length constraint"
print("ALL TESTS PASSED")
"""
    },
    {
        "id": "task_4_version_compare",
        "task": (
            "Write a function `compare_version_strings(v1: str, v2: str) -> int` that compares two semver-like version strings.\n"
            "Return 1 if v1 > v2, -1 if v1 < v2, and 0 if v1 == v2.\n"
            "Revision segments are separated by dots. Omitted segments count as 0 (e.g., '1.0' == '1.0.0').\n"
            "Include function definition and imports only."
        ),
        "test_harness": """
assert compare_version_strings("1.2", "1.10") == -1, "Failed: '1.2' should be smaller than '1.10'"
assert compare_version_strings("1.01", "1.001") == 0, "Failed: Leading zeros should evaluate equal"
assert compare_version_strings("1.0", "1.0.0.0") == 0, "Failed: Trailing zero segments should evaluate equal"
assert compare_version_strings("2.1", "2.01") == 0, "Failed: '2.1' and '2.01' should evaluate equal"
assert compare_version_strings("1.2.3", "1.2.4") == -1, "Failed: standard comparison"
print("ALL TESTS PASSED")
"""
    },
    {
        "id": "task_5_simple_eval",
        "task": (
            "Write a function `evaluate_expression(s: str) -> int` that evaluates a basic arithmetic string expression containing non-negative integers, '+', '-', '*', and '/'.\n"
            "Rules:\n"
            "1. Standard operator precedence applies ('*' and '/' before '+' and '-').\n"
            "2. Division must truncate toward zero (e.g., 3/2 = 1, -3/2 = -1).\n"
            "3. Do NOT use Python's built-in `eval()` or `exec()`.\n"
            "4. Spaces may appear throughout the expression.\n"
            "Include function definition and imports only."
        ),
        "test_harness": """
assert evaluate_expression("3+2*2") == 7, "Failed on precedence: 3+2*2"
assert evaluate_expression(" 3/2 ") == 1, "Failed on integer truncation: 3/2"
assert evaluate_expression(" 3+5 / 2 ") == 5, "Failed on combined precedence: 3+5/2"
assert evaluate_expression("14-3/2") == 13, "Failed on subtraction and division: 14-3/2"
assert evaluate_expression("0-2147483648") == -2147483648, "Failed on leading negative subtraction"
print("ALL TESTS PASSED")
"""
    }
]