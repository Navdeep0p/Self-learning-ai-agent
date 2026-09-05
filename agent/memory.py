import json
import math
import os
import requests

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

    def save_lesson(self, task: str, mistake: str, lesson: str):
        # Generate semantic vector for the task concept
        embedding = get_embedding(task)

        # Deduplication check using semantic similarity (>0.95 means identical meaning)
        for mem in self.memories:
            if "embedding" in mem and cosine_similarity(mem["embedding"], embedding) > 0.95:
                return

        entry = {
            "id": len(self.memories) + 1,
            "task": task.strip(),
            "mistake": mistake.strip(),
            "lesson": lesson.strip(),
            "embedding": embedding,
        }
        self.memories.append(entry)

        # Save to disk
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
            # Only match if they are truly in the same conceptual domain
            if sim >= threshold:
                scored.append((sim, mem["lesson"]))

        # Sort highest similarity first
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:top_k]]