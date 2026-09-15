import ollama
import numpy as np

MODEL = "embeddinggemma"

texts = [
    "Bäckerei Schneider",
    "Shell Tankstelle",
    "Jeans Fritz Kleidung",
    "Pänz & Piepmatz Spielwaren",
    "ALDI Supermarkt",
]


def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


embeddings = []

print("=" * 70)
print("EINZELNE OLLAMA EMBEDDINGS")
print("=" * 70)

for text in texts:
    response = ollama.embed(
        model=MODEL,
        input=text,
    )

    embedding = response["embeddings"][0]
    embeddings.append(embedding)

    print()
    print(f"TEXT: {text}")
    print(f"DIMENSION: {len(embedding)}")
    print("ERSTE 10 WERTE:")
    print(embedding[:10])


print()
print("=" * 70)
print("COSINE SIMILARITY")
print("=" * 70)

for i in range(len(texts)):
    for j in range(i + 1, len(texts)):
        similarity = cosine_similarity(
            embeddings[i],
            embeddings[j],
        )

        print(
            f"{similarity:.4f} | "
            f"{texts[i]} <-> {texts[j]}"
        )