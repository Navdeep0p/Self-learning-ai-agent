import json
import math
import os
import requests
from agent.llm import call_llm

MEMORY_FILE = "agent_memory.json"
OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"


def get_embedding(text: str) -> list[float]:
    """Generates a semantic vector embedding using Ollama."""
    try:
        response = requests.post(
            OLLAMA_EMBED_URL,
            json={"model": EMBED_MODEL, "prompt": text},
            timeout=30,
        )
        response.raise_for_status()
        return response.json().get("embedding", [])
    except Exception as e:
        print(f"[Memory Warning] Failed to generate embedding: {e}")
        return []


def cosine_similarity(v1: list[float], v2: list[float]) -> float:
    """Computes cosine similarity between two vectors."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot_product / (norm_a * norm_b)


class EpisodicMemory:
    def __init__(self, file_path=MEMORY_FILE):
        self.file_path = file_path
        self.memories = self._load()

    def _load(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _consolidate_rules(self, old_rule: str, new_rule: str) -> str:
        """Merges two semantically overlapping heuristics into a single actionable invariant."""
        prompt = f"""You are a knowledge consolidation engine for an autonomous coding agent.
Two similar programming rules have been identified. Synthesize them into a single, concise (1 sentence), high-signal coding invariant.

RULE A: {old_rule}
RULE B: {new_rule}

CONSOLIDATED INVARIANT:"""
        consolidated = call_llm(prompt).strip().split("\n")[0]
        # Clean formatting
        return consolidated.replace("`", "").strip()

    def save_lesson(self, task: str, mistake: str, lesson: str):
        embedding = get_embedding(task)
        if not embedding:
            return

        # Check existing memories for semantic similarity
        for idx, mem in enumerate(self.memories):
            stored_vector = mem.get("embedding", [])
            sim = cosine_similarity(stored_vector, embedding)

            # Case 1: Near-identical task/invariant -> Skip storing duplicate
            if sim > 0.94:
                return

            # Case 2: Closely related problem domain -> Consolidate into a stronger rule
            if sim >= 0.80:
                print(f"[Memory] Consolidating overlapping heuristic into Rule #{mem['id']}...")
                merged_rule = self._consolidate_rules(mem["lesson"], lesson)
                mem["lesson"] = merged_rule
                mem["task"] = f"{mem['task']}\nRelated: {task.strip()}"
                mem["embedding"] = get_embedding(mem["lesson"])

                with open(self.file_path, "w", encoding="utf-8") as f:
                    json.dump(self.memories, f, indent=2)
                print(f"[Memory] Updated Rule #{mem['id']}: {merged_rule}")
                return

        # Case 3: Distinct task -> Store as fresh memory
        entry = {
            "id": len(self.memories) + 1,
            "task": task.strip(),
            "mistake": mistake.strip(),
            "lesson": lesson.strip(),
            "embedding": embedding,
        }
        self.memories.append(entry)

        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.memories, f, indent=2)
        print(f"[Memory] Stored vector-indexed rule #{entry['id']} to {self.file_path}")

    def retrieve_relevant_lessons(self, current_task: str, top_k: int = 2, threshold: float = 0.70) -> list[str]:
        """Retrieves lessons strictly above the semantic similarity threshold."""
        if not self.memories:
            return []

        query_vector = get_embedding(current_task)
        if not query_vector:
            return []

        scored = []
        for mem in self.memories:
            stored_vector = mem.get("embedding", [])
            sim = cosine_similarity(query_vector, stored_vector)
            if sim >= threshold:
                scored.append((sim, mem["lesson"]))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:top_k]]