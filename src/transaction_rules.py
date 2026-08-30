from models import Transaction


def normalize_transaction(transaction: Transaction) -> Transaction:
    """
    Bestimmt die finanzielle Bedeutung einer Transaktion.
    """

    text = (
        f"{transaction.transaction_type} "
        f"{transaction.merchant} "
        f"{transaction.description}"
    ).lower()

    # ---------------------------------------------------------
    # Sparen
    # ---------------------------------------------------------

    savings_keywords = [
        "kleingeld plus",
        "kleingeld plus - sparen",
    ]

    if any(keyword in text for keyword in savings_keywords):
        transaction.normalized_type = "savings"
        transaction.is_internal_transfer = True
        return transaction

    # ---------------------------------------------------------
    # Hausdarlehen / Kredit
    # ---------------------------------------------------------

    loan_keywords = [
        "darlehen",
        "teilzahlung darlehen",
        "tilgung",
        "tilg.",
        "kredit",
    ]

    if any(keyword in text for keyword in loan_keywords):
        transaction.normalized_type = "loan_payment"
        return transaction

    # ---------------------------------------------------------
    # Gebühren
    # ---------------------------------------------------------

    fee_keywords = [
        "entgelt",
        "gebühr",
        "gebuehr",
        "kartengebühr",
        "kartengebuehr",
    ]

    if any(keyword in text for keyword in fee_keywords):
        transaction.normalized_type = "fee"
        return transaction

    # ---------------------------------------------------------
    # Interne Transfers über Lars Freier
    # ---------------------------------------------------------

    if "lars freier" in text:

        if transaction.amount > 0:
            transaction.normalized_type = "transfer_in"
        else:
            transaction.normalized_type = "transfer_out"

        transaction.is_internal_transfer = True
        return transaction

    # ---------------------------------------------------------
    # Weitere bekannte interne Transfers
    # ---------------------------------------------------------

    internal_transfer_keywords = [
        "übertrag auf girokonto",
        "uebertrag auf girokonto",
        "übertrag auf tagesgeld",
        "uebertrag auf tagesgeld",
        "eigenes konto",
    ]

    if any(
        keyword in text
        for keyword in internal_transfer_keywords
    ):
        if transaction.amount > 0:
            transaction.normalized_type = "transfer_in"
        else:
            transaction.normalized_type = "transfer_out"

        transaction.is_internal_transfer = True
        return transaction

    # ---------------------------------------------------------
    # Positive Beträge
    # ---------------------------------------------------------

    if transaction.amount > 0:

        # Rückerstattungen
        refund_keywords = [
            "rückerstattung",
            "rueckerstattung",
            "refund",
            "erstattung",
        ]

        if any(keyword in text for keyword in refund_keywords):
            transaction.normalized_type = "refund"
            return transaction

        # Bekannte Einkommensquellen
        income_keywords = [
            "zahlung aus dem ausland",
            "gehalt",
            "lohn",
            "salary",
            "betriebskrankenkasse",
            "krankenkasse",

            # Explizit bekannte Gutschrift
            "yvonne mertens",
        ]

        if any(keyword in text for keyword in income_keywords):
            transaction.normalized_type = "income"
            return transaction

        # Positive Amazon-Buchungen als Rückerstattung behandeln
        if "amazon payments europe" in text:
            transaction.normalized_type = "refund"
            return transaction

        transaction.normalized_type = "unknown_inflow"
        return transaction

    # ---------------------------------------------------------
    # Negative Beträge
    # ---------------------------------------------------------

    if transaction.amount < 0:
        transaction.normalized_type = "expense"
        return transaction

    # ---------------------------------------------------------
    # Nullbetrag
    # ---------------------------------------------------------

    transaction.normalized_type = "unknown"

    return transaction