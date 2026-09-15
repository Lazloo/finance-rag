from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import chromadb

from embeddings import create_embeddings, create_embedding
from text_cleaner import clean_transaction_text


DATA_FILE = Path("data/processed/transactions.json")
DB_DIR = Path("database")

COLLECTION_NAME = "transactions"
EMBEDDING_MODEL = "embeddinggemma"


def load_transactions() -> list[dict]:
    import json

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Datensatz nicht gefunden: {DATA_FILE}"
        )

    with DATA_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_document(transaction: dict) -> str:
    merchant = (
        transaction.get("merchant_normalized")
        or transaction.get("merchant")
        or ""
    )

    description = clean_transaction_text(
        transaction.get("description", "")
    )

    parts = [
        str(merchant).strip(),
        str(description).strip(),
    ]

    return " | ".join(
        part for part in parts
        if part
    )


def build_client():
    return chromadb.PersistentClient(
        path=str(DB_DIR)
    )


def build_collection(client):
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        configuration={
            "hnsw": {
                "space": "cosine",
            }
        },
    )


def build_vector_store():
    transactions = load_transactions()

    rag_transactions = [
        transaction
        for transaction in transactions
        if transaction.get("normalized_type") == "expense"
        and transaction.get("category")
        and transaction.get("category") != "Sonstiges"
    ]

    print(
        f"Transaktionen insgesamt: {len(transactions)}"
    )
    print(
        f"Für RAG geeignet: {len(rag_transactions)}"
    )

    documents = [
        build_document(transaction)
        for transaction in rag_transactions
    ]

    print("Erzeuge Embeddings...")

    embeddings = create_embeddings(documents)

    client = build_client()

    # Alte Collection komplett entfernen,
    # damit garantiert keine alten Embeddings übrig bleiben.
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = build_collection(client)

    ids = []
    metadatas = []

    for index, transaction in enumerate(rag_transactions):
        transaction_id = f"transaction-{index}"

        merchant_normalized = (
            transaction.get("merchant_normalized")
            or transaction.get("merchant")
            or ""
        )

        ids.append(transaction_id)

        metadatas.append(
            {
                "bank": str(transaction.get("bank", "")),
                "booking_date": str(
                    transaction.get("booking_date", "")
                ),
                "amount": float(
                    transaction.get("amount", 0)
                ),
                "transaction_type": str(
                    transaction.get("transaction_type", "")
                ),
                "normalized_type": str(
                    transaction.get("normalized_type", "")
                ),
                "merchant": str(
                    transaction.get("merchant", "")
                ),
                "merchant_normalized": str(
                    merchant_normalized
                ),
                "category": str(
                    transaction.get("category", "")
                ),
                "subcategory": str(
                    transaction.get("subcategory", "")
                ),
                "category_source": str(
                    transaction.get("category_source", "")
                ),
            }
        )

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    print(
        f"ChromaDB aufgebaut: {collection.count()} Einträge"
    )

    return collection


def normalize_search_text(text: str) -> str:
    return clean_transaction_text(
        text.strip().lower()
    )


def exact_merchant_search(
    collection,
    query: str,
    limit: int = 10,
) -> list[dict]:
    """
    Sucht zuerst nach einem exakten normalisierten Händlernamen.

    Chroma unterstützt hier keine direkte case-insensitive
    String-Suche über unsere Metadaten. Deshalb holen wir
    die Metadaten und filtern lokal.
    """

    normalized_query = normalize_search_text(query)

    result = collection.get(
        include=["metadatas", "documents"]
    )

    matches = []

    metadatas = result.get("metadatas") or []
    documents = result.get("documents") or []
    ids = result.get("ids") or []

    for transaction_id, metadata, document in zip(
        ids,
        metadatas,
        documents,
    ):
        merchant = normalize_search_text(
            str(
                metadata.get(
                    "merchant_normalized",
                    ""
                )
            )
        )

        if not merchant:
            continue

        if merchant == normalized_query:
            matches.append(
                {
                    "id": transaction_id,
                    "distance": 0.0,
                    "merchant": metadata.get(
                        "merchant_normalized"
                    ),
                    "category": metadata.get(
                        "category"
                    ),
                    "subcategory": metadata.get(
                        "subcategory"
                    ),
                    "booking_date": metadata.get(
                        "booking_date"
                    ),
                    "amount": metadata.get(
                        "amount"
                    ),
                    "document": document,
                    "match_type": "exact",
                }
            )

    return matches[:limit]


def semantic_search(
    collection,
    query: str,
    limit: int = 5,
) -> list[dict]:
    embedding = create_embedding(query)

    result = collection.query(
        query_embeddings=[embedding],
        n_results=limit,
        include=[
            "metadatas",
            "documents",
            "distances",
        ],
    )

    ids = result.get("ids", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    documents = result.get("documents", [[]])[0]
    distances = result.get("distances", [[]])[0]

    matches = []

    for (
        transaction_id,
        metadata,
        document,
        distance,
    ) in zip(
        ids,
        metadatas,
        documents,
        distances,
    ):
        matches.append(
            {
                "id": transaction_id,
                "distance": float(distance),
                "merchant": metadata.get(
                    "merchant_normalized"
                )
                or metadata.get("merchant"),
                "category": metadata.get(
                    "category"
                ),
                "subcategory": metadata.get(
                    "subcategory"
                ),
                "booking_date": metadata.get(
                    "booking_date"
                ),
                "amount": metadata.get(
                    "amount"
                ),
                "document": document,
                "match_type": "semantic",
            }
        )

    return matches

def infer_category_from_similar_transactions(
    collection,
    query: str,
    semantic_limit: int = 8,
    max_distance: float = 0.50,
    min_category_share: float = 0.70,
    min_supporting_matches: int = 2,
) -> dict:
    """
    Leitet eine Kategorie aus semantisch ähnlichen historischen
    Transaktionen ab.

    Eine Kategorie wird nur dann übernommen, wenn die Evidenz
    ausreichend stark ist.

    Bedingungen:
    - Treffer müssen <= max_distance sein
    - mindestens min_supporting_matches Treffer
    - eine Kategorie muss mindestens min_category_share
      der relevanten Treffer stellen

    Andernfalls wird bewusst keine Kategorie inferiert.
    """

    matches = semantic_search(
        collection,
        query,
        limit=semantic_limit,
    )

    relevant_matches = [
        match
        for match in matches
        if match["distance"] <= max_distance
        and match.get("category")
        and match["category"] != "Sonstiges"
    ]

    if not relevant_matches:
        return {
            "query": query,
            "category": None,
            "subcategory": None,
            "confidence": 0.0,
            "match_count": 0,
            "supporting_matches": 0,
            "matches": [],
            "reason": (
                "Keine ausreichend ähnlichen historischen "
                "Transaktionen gefunden."
            ),
        }

    category_counts = defaultdict(int)

    for match in relevant_matches:
        category_counts[match["category"]] += 1

    sorted_categories = sorted(
        category_counts.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    top_category, top_count = sorted_categories[0]
    total_count = len(relevant_matches)

    category_share = top_count / total_count

    # Zu wenig historische Evidenz
    if top_count < min_supporting_matches:
        return {
            "query": query,
            "category": None,
            "subcategory": None,
            "confidence": category_share,
            "match_count": total_count,
            "supporting_matches": top_count,
            "matches": relevant_matches,
            "reason": (
                f"Zu wenig Evidenz: Kategorie "
                f"'{top_category}' wird nur von "
                f"{top_count} historischen Treffer(n) gestützt."
            ),
        }

    # Kein ausreichender Konsens
    if category_share < min_category_share:
        return {
            "query": query,
            "category": None,
            "subcategory": None,
            "confidence": category_share,
            "match_count": total_count,
            "supporting_matches": top_count,
            "matches": relevant_matches,
            "reason": (
                f"Kein ausreichender Kategorie-Konsens. "
                f"'{top_category}' hat "
                f"{top_count}/{total_count} relevante Treffer "
                f"({category_share:.0%})."
            ),
        }

    # Die besten Treffer der gewählten Kategorie
    category_matches = [
        match
        for match in relevant_matches
        if match["category"] == top_category
    ]

    subcategory_counts = defaultdict(int)

    for match in category_matches:
        subcategory = match.get("subcategory")

        if subcategory:
            subcategory_counts[subcategory] += 1

    top_subcategory = None

    if subcategory_counts:
        top_subcategory = max(
            subcategory_counts,
            key=subcategory_counts.get,
        )

    return {
        "query": query,
        "category": top_category,
        "subcategory": top_subcategory,
        "confidence": category_share,
        "match_count": total_count,
        "supporting_matches": top_count,
        "matches": relevant_matches,
        "reason": (
            f"Kategorie '{top_category}' wird von "
            f"{top_count}/{total_count} relevanten "
            f"historischen Treffern gestützt "
            f"({category_share:.0%})."
        ),
    }

def print_category_inference(result: dict):
    print()
    print("=" * 80)
    print(
        f"KATEGORIE-INFERENZ: {result['query']}"
    )
    print("=" * 80)

    if result["category"] is None:
        print()
        print("Keine sichere Kategorie erkannt.")
        print(
            f"Grund: {result['reason']}"
        )
    else:
        print()
        print(
            f"Kategorie: {result['category']}"
        )

        if result["subcategory"]:
            print(
                f"Unterkategorie: "
                f"{result['subcategory']}"
            )

        print(
            f"Konfidenz: "
            f"{result['confidence']:.0%}"
        )

        print(
            f"Relevante historische Treffer: "
            f"{result['match_count']}"
        )

        print(
            f"Treffer für vorgeschlagene Kategorie: "
            f"{result['supporting_matches']}"
        )

        print(
            f"Begründung: {result['reason']}"
        )

    if result["matches"]:
        print()
        print("VERWENDETE ÄHNLICHE TRANSAKTIONEN")
        print("-" * 80)

        for index, match in enumerate(
            result["matches"],
            start=1,
        ):
            print(
                f"{index}. "
                f"{match['merchant']} | "
                f"{match['category']} | "
                f"{match['distance']:.4f}"
            )

def hybrid_search(
    collection,
    query: str,
    exact_limit: int = 10,
    semantic_limit: int = 5,
) -> dict:
    """
    Hybrid-Suche:

    1. Exakter normalisierter Händler-Match
    2. Falls kein exakter Treffer existiert:
       semantische Suche
    """

    exact_matches = exact_merchant_search(
        collection,
        query,
        limit=exact_limit,
    )

    # Bekannter Händler:
    # Exakte Treffer sind ausreichend.
    if exact_matches:
        return {
            "query": query,
            "match_type": "exact",
            "exact": exact_matches,
            "semantic": [],
        }

    # Unbekannter Händler:
    # Semantische Suche als Fallback.
    semantic_matches = semantic_search(
        collection,
        query,
        limit=semantic_limit,
    )

    return {
        "query": query,
        "match_type": "semantic",
        "exact": [],
        "semantic": semantic_matches,
    }


def print_hybrid_results(results: dict):
    print()
    print("=" * 80)
    print(f"HYBRID-SUCHE: {results['query']}")
    print("=" * 80)

    if results["match_type"] == "exact":

        print()
        print("EXAKTER HÄNDLER-MATCH")
        print("-" * 80)

        grouped = defaultdict(list)

        for match in results["exact"]:
            grouped[
                (
                    match["merchant"],
                    match["category"],
                    match["subcategory"],
                )
            ].append(match)

        for (
            merchant,
            category,
            subcategory,
        ), matches in grouped.items():

            print()
            print(f"Händler: {merchant}")
            print(f"Kategorie: {category}")

            if subcategory:
                print(
                    f"Unterkategorie: {subcategory}"
                )

            print(
                f"Historische Treffer: {len(matches)}"
            )

            amounts = [
                match["amount"]
                for match in matches
                if isinstance(
                    match["amount"],
                    (int, float),
                )
            ]

            if amounts:
                print(
                    f"Summe: {sum(amounts):.2f} €"
                )

            dates = [
                match["booking_date"]
                for match in matches
                if match["booking_date"]
            ]

            if dates:
                print(
                    f"Zeitraum: {min(dates)} bis {max(dates)}"
                )

    else:

        print()
        print("KEIN EXAKTER HÄNDLER")
        print("-" * 80)

        print(
            "Semantische Suche wird als Fallback verwendet."
        )

        for index, match in enumerate(
            results["semantic"],
            start=1,
        ):
            print()
            print(f"Treffer {index}")
            print(
                f"Distanz: {match['distance']:.4f}"
            )
            print(
                f"Händler: {match['merchant']}"
            )
            print(
                f"Kategorie: {match['category']}"
            )

            if match["subcategory"]:
                print(
                    f"Unterkategorie: {match['subcategory']}"
                )

            print(
                f"Datum: {match['booking_date']}"
            )

            print(
                f"Betrag: {match['amount']:.2f} €"
            )


def get_collection():
    client = build_client()

    try:
        collection = client.get_collection(
            COLLECTION_NAME
        )
    except Exception as exc:
        raise RuntimeError(
            "Chroma Collection existiert nicht. "
            "Bitte zuerst vector_store.py ausführen."
        ) from exc

    return collection


if __name__ == "__main__":
    build_vector_store()