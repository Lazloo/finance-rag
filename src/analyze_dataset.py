from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


DATA_FILE = Path(
    "data/processed/transactions.json"
)


def load_transactions() -> list[dict]:
    """Lädt die verarbeiteten Transaktionen aus der JSON-Datei."""

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Datei nicht gefunden: {DATA_FILE}"
        )

    return json.loads(
        DATA_FILE.read_text(
            encoding="utf-8"
        )
    )


def format_eur(amount: float) -> str:
    """Formatiert einen Betrag im deutschen Zahlenformat."""

    return f"{amount:,.2f}".replace(
        ",", "X"
    ).replace(
        ".", ","
    ).replace(
        "X", "."
    )


def print_transaction(
    transaction: dict,
) -> None:
    """Gibt eine einzelne Transaktion kompakt aus."""

    print(
        f"  {transaction['booking_date']} | "
        f"{transaction['merchant'][:45]:45} | "
        f"{format_eur(transaction['amount']):>12} €"
    )


def main() -> None:

    transactions = load_transactions()

    print("=" * 70)
    print("DATA QUALITY REPORT")
    print("=" * 70)

    # =========================================================
    # Gesamtzahl
    # =========================================================

    print(
        f"\nTransaktionen insgesamt: "
        f"{len(transactions)}"
    )

    # =========================================================
    # Banken
    # =========================================================

    banks = Counter(
        transaction.get(
            "bank",
            "UNBEKANNT",
        )
        for transaction in transactions
    )

    print("\nNach Bank:")

    for bank, count in banks.most_common():

        print(
            f"  {bank}: {count}"
        )

    # =========================================================
    # Originale Transaktionstypen
    # =========================================================

    transaction_types = Counter(
        transaction.get(
            "transaction_type",
            "UNBEKANNT",
        )
        for transaction in transactions
    )

    print(
        "\nNach Transaktionstyp:"
    )

    for transaction_type, count in (
        transaction_types.most_common()
    ):

        print(
            f"  {transaction_type}: {count}"
        )

    # =========================================================
    # Normalisierte Typen
    # =========================================================

    normalized_types = Counter(
        transaction.get(
            "normalized_type",
            "unknown",
        )
        for transaction in transactions
    )

    print(
        "\nNormalisierte Typen:"
    )

    for normalized_type, count in (
        normalized_types.most_common()
    ):

        print(
            f"  {normalized_type}: {count}"
        )

    # =========================================================
    # Finanzielle Kennzahlen
    # =========================================================

    income = sum(
        transaction["amount"]
        for transaction in transactions
        if transaction.get(
            "normalized_type"
        ) == "income"
    )

    refunds = sum(
        transaction["amount"]
        for transaction in transactions
        if transaction.get(
            "normalized_type"
        ) == "refund"
    )

    expenses = sum(
        transaction["amount"]
        for transaction in transactions
        if transaction.get(
            "normalized_type"
        ) == "expense"
    )

    loan_payments = sum(
        transaction["amount"]
        for transaction in transactions
        if transaction.get(
            "normalized_type"
        ) == "loan_payment"
    )

    fees = sum(
        transaction["amount"]
        for transaction in transactions
        if transaction.get(
            "normalized_type"
        ) == "fee"
    )

    savings = sum(
        transaction["amount"]
        for transaction in transactions
        if transaction.get(
            "normalized_type"
        ) == "savings"
    )

    transfer_in = sum(
        transaction["amount"]
        for transaction in transactions
        if transaction.get(
            "normalized_type"
        ) == "transfer_in"
    )

    transfer_out = sum(
        transaction["amount"]
        for transaction in transactions
        if transaction.get(
            "normalized_type"
        ) == "transfer_out"
    )

    unknown_inflow = sum(
        transaction["amount"]
        for transaction in transactions
        if transaction.get(
            "normalized_type"
        ) == "unknown_inflow"
    )

    # =========================================================
    # Bereinigter Cashflow
    # =========================================================

    # Interne Transfers und Spartransfers werden hier
    # bewusst NICHT berücksichtigt.
    #
    # Einnahmen
    # + Rückerstattungen
    # + unbekannte externe Eingänge
    # + normale Ausgaben (negativ)
    # + Darlehen (negativ)
    # + Gebühren (negativ)

    adjusted_balance = (
        income
        + refunds
        + unknown_inflow
        + expenses
        + loan_payments
        + fees
    )

    print("\nFinanzen:")

    print(
        f"  Einkommen             : "
        f"{format_eur(income)} €"
    )

    print(
        f"  Rückerstattungen      : "
        f"{format_eur(refunds)} €"
    )

    print(
        f"  Konsumausgaben        : "
        f"{format_eur(expenses)} €"
    )

    print(
        f"  Hausdarlehen          : "
        f"{format_eur(loan_payments)} €"
    )

    print(
        f"  Gebühren              : "
        f"{format_eur(fees)} €"
    )

    print(
        f"  Spartransfers         : "
        f"{format_eur(savings)} €"
    )

    print(
        f"  Interne Transfers rein: "
        f"{format_eur(transfer_in)} €"
    )

    print(
        f"  Interne Transfers raus: "
        f"{format_eur(transfer_out)} €"
    )

    internal_movements = (
        savings
        + transfer_in
        + transfer_out
    )

    print(
        f"  Interne Bewegungen    : "
        f"{format_eur(internal_movements)} €"
    )

    print(
        f"  Unbekannte Eingänge   : "
        f"{format_eur(unknown_inflow)} €"
    )

    print(
        f"  Bereinigter Saldo     : "
        f"{format_eur(adjusted_balance)} €"
    )

    # =========================================================
    # Datenqualität
    # =========================================================

    missing_merchant = [
        transaction
        for transaction in transactions
        if not transaction.get(
            "merchant"
        )
        or not transaction[
            "merchant"
        ].strip()
    ]

    missing_date = [
        transaction
        for transaction in transactions
        if not transaction.get(
            "booking_date"
        )
    ]

    missing_type = [
        transaction
        for transaction in transactions
        if not transaction.get(
            "transaction_type"
        )
    ]

    print("\nFehlende Daten:")

    print(
        f"  Händler: "
        f"{len(missing_merchant)}"
    )

    print(
        f"  Datum  : "
        f"{len(missing_date)}"
    )

    print(
        f"  Ohne Transaktionstyp: "
        f"{len(missing_type)}"
    )

    # =========================================================
    # Konsumausgaben nach Kategorie
    # =========================================================

    categories = Counter(
        transaction.get(
            "category",
            "Unbekannt",
        )
        for transaction in transactions
        if transaction.get(
            "normalized_type"
        ) == "expense"
    )

    print(
        "\nKonsumausgaben nach Kategorie:"
    )

    if not categories:

        print(
            "  Keine kategorisierten "
            "Konsumausgaben gefunden."
        )

    else:

        for category, count in (
            categories.most_common()
        ):

            total = sum(
                transaction["amount"]
                for transaction in transactions
                if (
                    transaction.get(
                        "normalized_type"
                    ) == "expense"
                    and transaction.get(
                        "category",
                        "Unbekannt",
                    ) == category
                )
            )

            print(
                f"  {category:25} "
                f"{format_eur(total):>12} € "
                f"({count} Buchungen)"
            )

    # =========================================================
    # Größte Konsumausgaben
    # =========================================================

    biggest_expenses = sorted(
        [
            transaction
            for transaction in transactions
            if transaction.get(
                "normalized_type"
            ) == "expense"
        ],
        key=lambda transaction: (
            transaction["amount"]
        ),
    )[:10]

    print(
        "\n10 größte Konsumausgaben:"
    )

    for transaction in biggest_expenses:
        print_transaction(transaction)

    # =========================================================
    # Darlehenszahlungen
    # =========================================================

    biggest_loan_payments = sorted(
        [
            transaction
            for transaction in transactions
            if transaction.get(
                "normalized_type"
            ) == "loan_payment"
        ],
        key=lambda transaction: (
            transaction["amount"]
        ),
    )

    print(
        "\nDarlehenszahlungen:"
    )

    if not biggest_loan_payments:

        print("  Keine gefunden.")

    else:

        for transaction in biggest_loan_payments:
            print_transaction(transaction)

    # =========================================================
    # Einkommen
    # =========================================================

    biggest_income = sorted(
        [
            transaction
            for transaction in transactions
            if transaction.get(
                "normalized_type"
            ) == "income"
        ],
        key=lambda transaction: (
            transaction["amount"]
        ),
        reverse=True,
    )[:10]

    print(
        "\n10 größte Einkommen:"
    )

    if not biggest_income:

        print("  Keine gefunden.")

    else:

        for transaction in biggest_income:
            print_transaction(transaction)

    # =========================================================
    # Rückerstattungen
    # =========================================================

    refund_transactions = sorted(
        [
            transaction
            for transaction in transactions
            if transaction.get(
                "normalized_type"
            ) == "refund"
        ],
        key=lambda transaction: (
            transaction["amount"]
        ),
        reverse=True,
    )

    print(
        "\nRückerstattungen:"
    )

    if not refund_transactions:

        print("  Keine gefunden.")

    else:

        for transaction in refund_transactions:
            print_transaction(transaction)

    # =========================================================
    # Unbekannte Eingänge
    # =========================================================

    unknown_transactions = sorted(
        [
            transaction
            for transaction in transactions
            if transaction.get(
                "normalized_type"
            ) == "unknown_inflow"
        ],
        key=lambda transaction: (
            transaction["amount"]
        ),
        reverse=True,
    )

    print(
        "\nUnbekannte Eingänge:"
    )

    if not unknown_transactions:

        print("  Keine gefunden.")

    else:

        for transaction in unknown_transactions:
            print_transaction(transaction)

    print("\nKI-Klassifizierungen:")

    llm_transactions = [
        transaction
        for transaction in transactions
        if transaction.get("category_source") == "ollama"
    ]

    if not llm_transactions:
        print("  Keine.")

    else:
        for transaction in llm_transactions:
            print(
                f"  {transaction['booking_date']} | "
                f"{transaction['merchant'][:40]} | "
                f"{transaction['category']} | "
                f"Confidence: "
                f"{transaction['category_confidence']:.2f}"
            )
            print(
                f"    {transaction.get('category_reason', '')}"
            )


if __name__ == "__main__":
    main()