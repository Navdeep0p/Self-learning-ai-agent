
# Autonomous Self-Learning Coding Agent

A local, autonomous Python software engineering agent featuring recursive error correction (**Reflexion**) and persistent cross-task knowledge transfer (**Dense Vector Episodic Memory**).

The system runs entirely locally via **Ollama**, pairing `qwen2.5-coder:7b` for code synthesis and debugging with `nomic-embed-text` for semantic retrieval. Zero cloud APIs, zero external inference costs, fully reproducible.

---

## ⚡ Key Highlights

- **Reflexion Loop:** Catches test assertions, runtime exceptions, and syntax failures in an isolated execution sandbox, analyzes line-annotated tracebacks, and generates structured repairs.
- **Invariant Distillation:** Converts bug diagnoses into generalized, forward-looking programming rules rather than superficial line-number comments.
- **Dense Semantic Retrieval:** Replaces brittle keyword/Jaccard matching with cosine similarity over 768-dimensional embeddings, preventing context contamination across unrelated tasks.
- **Zero-Shot Heuristic Transfer:** Automatically injects previously learned edge-case invariants when a similar task is encountered, turning multi-attempt failures into single-pass successes.
- **Passive-Thermal Friendly:** Tuned for hardware with limited thermal headroom (e.g., Apple Silicon MacBook Air) with controlled generation budgets and inter-task pacing.

---

## 🏗️ Architecture

```


              ┌───────────────────────────────┐
              │          Task Prompt          │
              └──────────────┬────────────────┘
                             │
                             ▼



┌──────────────────┐    Cosine Similarity >= 0.70  ┌───────────────────────────┐
│ agent_memory.json│ ◄───────────────────────────► │  Dense Vector Retrieval   │
└──────────────────┘     (nomic-embed-text)        └─────────────┬─────────────┘
│ Relevant
│ Invariants
▼
┌───────────────────────────┐
│    Code Generator Engine  │
│    (qwen2.5-coder:7b)     │
└─────────────┬─────────────┘
│ Function Code
▼
┌───────────────────────────┐
│    Execution Sandbox      │
│   (Isolated Unit Tests)   │
└──────┬─────────────┬──────┘
│             │
Pass          │ Fail (Traceback)
│             ▼
│    ┌───────────────────────────┐
│    │     Reflector Module      │
│    │ (Root Cause -> Invariant) │
│    └────────────┬──────────────┘
│                 │
│                 ├─► Repaired Code
│                 │   (Next Trial Run)
│                 ▼
│    ┌───────────────────────────┐
│    │   Vector Embeddings       │
│    │   (nomic-embed-text)      │
│    └────────────┬──────────────┘
│                 │ Persist Rule
│                 ▼
│    ┌───────────────────────────┐
└───►│   Task Complete & Saved   │
     └───────────────────────────┘

```

---

## 📁 Repository Structure

```text
.
├── agent/
│   ├── __init__.py
│   ├── benchmark.py       # Evaluation suite with hidden assert harnesses
│   ├── executor.py        # Sandboxed execution environment
│   ├── llm.py             # Ollama API interface and prompt engineering
│   ├── memory.py          # Vector store and cosine similarity search
│   └── reflector.py       # Traceback analysis and invariant distillation
├── agent_memory.json      # Persistent vector-indexed heuristic store
├── main.py                # Agent orchestrator and benchmark driver
├── requirements.txt       # Project dependencies
└── README.md

```

---

## ⚙️ Core Modules

| Component | File | Mechanism |
| --- | --- | --- |
| **Generation** | `agent/llm.py` | Prompts `qwen2.5-coder:7b` with injected invariants; isolates code blocks from prose. |
| **Sandbox** | `agent/executor.py` | Executes combined solution + test harness in an isolated subprocess; captures `stdout`, `stderr`, and exit codes. |
| **Reflector** | `agent/reflector.py` | Formats code with explicit line numbers, inspects tracebacks, extracts a distilled `RULE:`, and repairs logic. |
| **Episodic Memory** | `agent/memory.py` | Generates semantic vectors via `nomic-embed-text`, deduplicates rules at >0.95 similarity, and retrieves top matches at >=0.70 threshold. |
| **Benchmark Suite** | `agent/benchmark.py` | Houses test harnesses covering boundary constraints, algorithmic sequences, and edge-case inputs. |

---

## 🚀 Quickstart

### Prerequisites

* Python 3.10+
* [Ollama](https://ollama.com/) installed and running locally

### 1. Download Local Models

```bash
ollama pull qwen2.5-coder:7b
ollama pull nomic-embed-text

```

### 2. Environment Setup

```bash
# Clone the repository
git clone [https://github.com/](https://github.com/)<your-username>/Self-learning-ai-agent.git
cd Self-learning-ai-agent

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

```

### 3. Run the Agent Loop

Ensure the Ollama daemon is running (`ollama serve`), then start the benchmark:

```bash
python main.py

```

---

## 🧪 Benchmark Suite

The built-in benchmark validates the agent against diverse algorithmic and edge-case tasks:

1. **`task_1_valid_parentheses`**: Balanced delimiter verification via stack.
2. **`task_2_longest_consecutive`**: Linear-time sequence tracking over unsorted, duplicate-laden input.
3. **`task_3_truncate_words`**: Boundary-safe text clipping with strict ellipsis length constraints.
4. **`task_4_version_compare`**: Multi-segment semver comparisons with leading/trailing zero normalization.
5. **`task_5_simple_eval`**: Mathematical expression evaluation with standard operator precedence and zero-truncation integer division (no `eval()`).

---

## 📈 Example Learning Run

```text
======================================================================
EVALUATING: task_3_truncate_words
======================================================================
[Attempt 1] Generating function...
--- RUN 1/3 ---
[-] FAILED on attempt 1.
[-] Error: AssertionError: Failed on length constraint
[Reflector] Repairing code against failed assertion...
[Diagnosis]: Always ensure that the length of the truncated string, including any appended ellipsis, does not exceed the specified maximum length.
--- RUN 2/3 ---
[+] PASSED on attempt 2!
[Memory] Stored vector-indexed rule #1 to agent_memory.json

======================================================================
SECOND PASS (RERUN AFTER LEARNING)
======================================================================
EVALUATING: task_3_truncate_words
[Memory] Injected 1 stored rule(s):
  1. Always ensure that the length of the truncated string, including any appended ellipsis, does not exceed the specified maximum length.
[Attempt 1] Generating function...
--- RUN 1/3 ---
[+] PASSED on attempt 1!  <-- Zero-shot transfer successful

```

---

## 📄 License

MIT License. Free to use, adapt, and build upon.