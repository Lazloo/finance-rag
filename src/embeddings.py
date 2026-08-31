from __future__ import annotations

import ollama


EMBEDDING_MODEL = "nomic-embed-text"


def create_embedding(text: str) -> list[float]:
    """
    Erstellt einen Embedding-Vektor für einen Text.
    """

    if not text.strip():
        raise ValueError(
            "Text für Embedding darf nicht leer sein."
        )

    response = ollama.embed(
        model=EMBEDDING_MODEL,
        input=text,
    )

    embeddings = response.get("embeddings")

    if not embeddings:
        raise RuntimeError(
            "Ollama hat kein Embedding zurückgegeben."
        )

    return embeddings[0]


def create_embeddings(
    texts: list[str],
) -> list[list[float]]:
    """
    Erstellt Embeddings für mehrere Texte.
    """

    if not texts:
        return []

    response = ollama.embed(
        model=EMBEDDING_MODEL,
        input=texts,
    )

    embeddings = response.get("embeddings")

    if embeddings is None:
        raise RuntimeError(
            "Ollama hat keine Embeddings zurückgegeben."
        )

    if len(embeddings) != len(texts):
        raise RuntimeError(
            "Anzahl der Embeddings stimmt nicht "
            "mit der Anzahl der Texte überein."
        )

    return embeddings