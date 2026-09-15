from vector_store import get_collection
from llm_categorizer import (
    categorize_transaction_with_rag,
)
import json


TEST_TRANSACTIONS = [
    {
        "merchant_normalized": "STICHTING MOLLIE PAYMENTS",
        "merchant": "STICHTING MOLLIE PAYMENTS",
        "description": (
            "RF11-8486-3003-9586 "
            "End-to-End-Ref.: nicht angegeben"
        ),
        "amount": -40.00,
    },
    {
        "merchant_normalized": "Transdev Vertrieb Gm",
        "merchant": "Transdev Vertrieb Gm",
        "description": (
            "VRR KORSCHENBOICH/Ladestr. 2/"
            "Korschenbroich/DE"
        ),
        "amount": -33.60,
    },
    {
        "merchant_normalized": "HORSTHEMKE BACKBETRIEBE",
        "merchant": "HORSTHEMKE BACKBETRIEBE",
        "description": (
            "HORSTHEMKE BACKBETRIEBE GIR"
        ),
        "amount": -8.15,
    },
    {
        "merchant_normalized": "Living de Luxe GmbH",
        "merchant": "LIVING DE LUXE GMBH",
        "description": (
            "CARWASH-DELUXE GMBH/"
            "ROBERT-BOSCH-STR. 2 A/"
            "KORSCHENBROICH/DE"
        ),
        "amount": -18.00,
    },
    {
        "merchant_normalized": "Dinner Catering GmbH",
        "merchant": "Dinner Catering GmbH",
        "description": "LB-1113 Mertens Clea",
        "amount": -60.00,
    },
    {
        "merchant_normalized": "Gemeinde Zeltingen-Rachtig",
        "merchant": "GEMEINDE ZELTINGEN-RAC",
        "description": (
            "ZELTINGEN-RACHTIG DE"
        ),
        "amount": -1.00,
    },
    {
        "merchant_normalized": "Heiko Grunert",
        "merchant": "HEIKO GRUNERT EK",
        "description": (
            "HEIKO GRUNERT EK, ASCHERSLEBEN DE"
        ),
        "amount": -79.07,
    },
]


def main():
    collection = get_collection()

    for transaction in TEST_TRANSACTIONS:
        print()
        print("=" * 80)
        print(
            transaction["merchant_normalized"]
        )
        print("=" * 80)

        result = categorize_transaction_with_rag(
            transaction,
            collection,
        )

        print(
            json.dumps(
                {
                    "category": result["category"],
                    "subcategory": result["subcategory"],
                    "confidence": result["confidence"],
                    "reason": result["reason"],
                    "rag_match_type": result[
                        "rag_match_type"
                    ],
                },
                ensure_ascii=False,
                indent=2,
            )
        )

        print()
        print("RAG-TREFFER:")

        for match in result["rag_matches"][:5]:
            print(
                f"  {match.get('merchant')} | "
                f"{match.get('category')} | "
                f"Distanz: {match.get('distance', 0):.4f}"
            )


if __name__ == "__main__":
    main()