from vector_store import (
    get_collection,
    hybrid_search,
    print_hybrid_results,
    infer_category_from_similar_transactions,
    print_category_inference,
)


KNOWN_QUERIES = [
    "Bäckerei Schneider",
    "Shell",
    "Jeans Fritz",
    "Pänz & Piepmatz",
    "Tankstelle",
]


UNKNOWN_QUERIES = [
    "Backerei Bernd",
    "Unbekannte Bäckerei",
    "Neue Tankstelle",
    "Unbekannter Kleidungsladen",
    "Neuer Spielwarenladen",
]


def main():
    collection = get_collection()

    print(
        f"Einträge in Chroma: {collection.count()}"
    )

    print()
    print("#" * 80)
    print("TEIL 1: BEKANNTE HÄNDLER")
    print("#" * 80)

    for query in KNOWN_QUERIES:
        results = hybrid_search(
            collection,
            query,
            exact_limit=10,
            semantic_limit=5,
        )

        print_hybrid_results(results)

    print()
    print()
    print("#" * 80)
    print("TEIL 2: UNBEKANNTE HÄNDLER")
    print("#" * 80)

    for query in UNKNOWN_QUERIES:
        result = infer_category_from_similar_transactions(
            collection,
            query,
            semantic_limit=8,
            max_distance=0.50,
            min_category_share=0.70,
            min_supporting_matches=2,
        )

        print_category_inference(result)


if __name__ == "__main__":
    main()