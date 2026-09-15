from __future__ import annotations

import json
from pathlib import Path

from llm_categorizer import categorize_transaction_with_rag
from vector_store import get_collection


DATA_FILE = Path("data/processed/transactions.json")
REVIEW_FILE = Path("data/processed/llm_review.json")


def load_transactions() -> list[dict]:
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Datensatz nicht gefunden: {DATA_FILE}"
        )

    with DATA_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_review(results: list[dict]) -> None:
    REVIEW_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with REVIEW_FILE.open("w", encoding="utf-8") as f:
        json.dump(
            results,
            f,
            ensure_ascii=False,
            indent=2,
        )


def main():
    transactions = load_transactions()

    sonstiges = [
        transaction
        for transaction in transactions
        if transaction.get("normalized_type") == "expense"
        and transaction.get("category") == "Sonstiges"
    ]

    collection = get_collection()

    review_results = []

    print("=" * 100)
    print(
        f"LLM-REVIEW: {len(sonstiges)} SONSTIGES-TRANSAKTIONEN"
    )
    print("=" * 100)

    for index, transaction in enumerate(
        sonstiges,
        start=1,
    ):
        merchant = (
            transaction.get("merchant_normalized")
            or transaction.get("merchant")
            or ""
        )

        date = transaction.get(
            "booking_date",
            "",
        )

        amount = float(
            transaction.get(
                "amount",
                0,
            )
        )

        description = (
            transaction.get(
                "description",
                "",
            )
            or ""
        )

        print()
        print()
        print("#" * 100)
        print(
            f"TRANSAKTION {index}/{len(sonstiges)}"
        )
        print("#" * 100)

        print(
            f"Datum       : {date}"
        )
        print(
            f"Händler     : {merchant}"
        )
        print(
            f"Betrag      : {amount:.2f} €"
        )
        print(
            f"Verwendung  : {description}"
        )

        try:
            result = categorize_transaction_with_rag(
                transaction,
                collection,
            )
        except Exception as exc:
            print()
            print("FEHLER BEI LLM-KLASSIFIZIERUNG")
            print(
                f"{type(exc).__name__}: {exc}"
            )

            review_results.append(
                {
                    "booking_date": date,
                    "merchant": merchant,
                    "amount": amount,
                    "old_category": "Sonstiges",
                    "llm_category": None,
                    "llm_subcategory": None,
                    "llm_confidence": None,
                    "llm_reason": "",
                    "rag_match_type": None,
                    "rag_matches": [],
                    "error": (
                        f"{type(exc).__name__}: {exc}"
                    ),
                }
            )

            continue

        llm_category = result.get(
            "category"
        )

        llm_subcategory = result.get(
            "subcategory"
        )

        llm_confidence = result.get(
            "confidence"
        )

        llm_reason = result.get(
            "reason",
            "",
        )

        rag_match_type = result.get(
            "rag_match_type"
        )

        rag_matches = result.get(
            "rag_matches",
            [],
        )

        review_results.append(
            {
                "booking_date": date,
                "merchant": merchant,
                "amount": amount,
                "old_category": "Sonstiges",
                "llm_category": llm_category,
                "llm_subcategory": llm_subcategory,
                "llm_confidence": llm_confidence,
                "llm_reason": llm_reason,
                "rag_match_type": rag_match_type,
                "rag_matches": rag_matches,
                "error": None,
            }
        )

        print()
        print("-" * 100)
        print("LLM-ERGEBNIS")
        print("-" * 100)

        print(
            f"Kategorie     : "
            f"{llm_category}"
        )

        print(
            f"Unterkategorie: "
            f"{llm_subcategory or ''}"
        )

        if llm_confidence is None:
            print(
                "Konfidenz     : unbekannt"
            )
        else:
            print(
                f"Konfidenz     : "
                f"{float(llm_confidence):.2f}"
            )

        print(
            f"RAG-Typ       : "
            f"{rag_match_type}"
        )

        print(
            f"Begründung    : "
            f"{llm_reason}"
        )

        print()
        print("-" * 100)
        print(
            f"RAG-TREFFER ({len(rag_matches)})"
        )
        print("-" * 100)

        if not rag_matches:
            print(
                "Keine historischen Treffer."
            )
        else:
            for match_index, match in enumerate(
                rag_matches[:6],
                start=1,
            ):
                print(
                    f"{match_index}. "
                    f"{match.get('merchant')} | "
                    f"{match.get('category')} | "
                    f"{match.get('subcategory') or ''} | "
                    f"Distanz: "
                    f"{match.get('distance', 0):.4f}"
                )

    save_review(review_results)

    print()
    print()
    print("=" * 100)
    print("REVIEW ABGESCHLOSSEN")
    print("=" * 100)

    print(
        f"Transaktionen geprüft : "
        f"{len(review_results)}"
    )

    successful = [
        result
        for result in review_results
        if result["error"] is None
    ]

    errors = [
        result
        for result in review_results
        if result["error"] is not None
    ]

    print(
        f"LLM erfolgreich        : "
        f"{len(successful)}"
    )

    print(
        f"Fehler                 : "
        f"{len(errors)}"
    )

    print()
    print(
        f"Review-Datei gespeichert:"
    )
    print(
        f"  {REVIEW_FILE}"
    )


if __name__ == "__main__":
    main()