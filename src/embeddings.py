from __future__ import annotations

import ollama

EMBEDDING_MODEL = "embeddinggemma"


def create_embedding(text: str) -> list[float]:
    if not text.strip():
        raise ValueError("Text darf nicht leer sein.")

    response = ollama.embed(
        model=EMBEDDING_MODEL,
        input=text,
    )

    embeddings = response.get("embeddings")

    if not embeddings:
        raise RuntimeError("Ollama hat kein Embedding zurückgegeben.")

    return embeddings[0]


def create_embeddings(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    response = ollama.embed(
        model=EMBEDDING_MODEL,
        input=texts,
    )

    embeddings = response.get("embeddings")

    if embeddings is None:
        raise RuntimeError("Ollama hat keine Embeddings zurückgegeben.")

    if len(embeddings) != len(texts):
        raise RuntimeError(
            f"Anzahl Embeddings ({len(embeddings)}) "
            f"passt nicht zu Anzahl Texte ({len(texts)})."
        )

    return embeddings