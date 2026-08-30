from __future__ import annotations

import json
from pathlib import Path


DATA_FILE = Path("data/processed/transactions.json")


def main():

    data = json.loads(
        DATA_FILE.read_text(encoding="utf-8")
    )

    print("=" * 100)
    print("POSITIVE TRANSACTIONS")
    print("=" * 100)

    for i, t in enumerate(data, start=1):

        if t["amount"] <= 0:
            continue

        print()
        print(f"#{i}")
        print(f"Bank       : {t['bank']}")
        print(f"Datum      : {t['booking_date']}")
        print(f"Typ        : {t['transaction_type']}")
        print(f"Merchant   : {t['merchant']}")
        print(f"Betrag     : {t['amount']:.2f} €")
        print(f"Beschreibung:")
        print(f"  {t['description']}")

    print()
    print("=" * 100)
    print("UNKNOWN TRANSACTION TYPES")
    print("=" * 100)

    for i, t in enumerate(data, start=1):

        if t["transaction_type"] == "Unbekannt":

            print()
            print(f"#{i}")
            print(t)


if __name__ == "__main__":
    main()