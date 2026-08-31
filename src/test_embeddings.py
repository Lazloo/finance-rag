from embeddings import create_embeddings


texts = [
    "LIDL Supermarkt Lebensmittel Einkauf",
    "REWE Lebensmittel Supermarkt Einkauf",
    "Shell Tankstelle Benzin Auto",
]


embeddings = create_embeddings(texts)

print(
    f"{len(embeddings)} Embeddings erstellt."
)

for i, embedding in enumerate(embeddings):
    print(
        f"Text {i + 1}: "
        f"{len(embedding)} Dimensionen"
    )