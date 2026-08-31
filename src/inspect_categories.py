from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path


DATA_FILE = Path(
    "data/processed/transactions.json"
)


def main():
    data = json.loads(
        DATA_FILE.read_text(
            encoding="utf-8"
        )
    )

    uncategorized = [
        transaction
        for transaction in data
        if (
            transaction.get("normalized_type") == "expense"
            and transaction.get("category") == "Sonstiges"
        )
    ]

    print("=" * 100)
    print(
        f"SONSTIGE AUSGABEN "
        f"({len(uncategorized)} Buchungen)"
    )
    print("=" * 100)

    total = 0.0

    for transaction in uncategorized:
        amount = transaction["amount"]
        total += amount

        print()
        print(
            f"{transaction['booking_date']} | "
            f"{amount:>10.2f} €"
        )
        print(
            f"Händler: {transaction['merchant']}"
        )
        print(
            f"Typ:     {transaction['transaction_type']}"
        )
        print(
            f"Text:    {transaction['description']}"
        )

    print()
    print("=" * 100)
    print(
        f"Summe Sonstiges: {total:.2f} €"
    )


if __name__ == "__main__":
    main()