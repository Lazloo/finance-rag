from __future__ import annotations

from models import Transaction


# =========================================================
# Kategorie-Regeln
# =========================================================
#
# Die Reihenfolge ist wichtig.
# Spezifischere Regeln stehen vor allgemeineren Regeln.
#
# Gesucht wird in:
#   - merchant
#   - transaction_type
#   - description
#
# =========================================================

CATEGORY_RULES = {
    "Lebensmittel": [
        "rewe",
        "edeka",
        "lidl",
        "aldi",
        "meinaldi",
        "netto",
        "picnic",
        "trinkgut",
        "frischecenter",
        "frischec",
        "büsch fil",
        "buesch fil",
        "kamps",
        "landbaeckerei stinges",
        "stinges",
        "supermarkt",
        "lebensmittel",
    ],

    "Drogerie": [
        "dm drogerie",
        "dm-drogerie",
        "drogeriemarkt",
        "rossmann",
    ],

    "Gesundheit": [
        "maxmo",
        "apotheke",
        "arzt",
        "ärzt",
        "aerzt",
        "zahnarzt",
        "krankenhaus",
        "klinik",
        "bleck, dau",
        "bleck dau",
        "versin",
    ],

    "Kinder": [
        "essensgeld",
        "kindertanz",
        "kindergarten",
        "kita",
        "schule",
        "schultuete",
        "schultüte",
        "smyths toys",
        "buch und spielkiste",
        "spielkiste",
        "ernstings",
        "paenz",
        "pä nz",
        "piepmatz",
    ],

    "Mobilität": [
        "shell deutschland",
        "shell",
        "aral",
        "esso",
        "tankstelle",
        "deutsche tamoil",
        "tamoil",
        "auto service",
        "autowerkstatt",
        "parking",
        "parkg.",
        "parkgebühr",
        "parkgebuehr",
        "parkplatz",
    ],

    "Wohnen": [
        "new energie",
        "energie",
        "strom",
        "gas",
        "miete",
        "wohnung",
        "deutsche glasfaser",
        "glasfaser",
    ],

    "Telekommunikation": [
        "deutsche glasfaser",
        "glasfaser",
        "telekom",
        "vodafone",
        "o2",
        "telefonica",
    ],

    "Reisen": [
        "belvilla",
        "fewodirekt",
        "ferienwohnung",
        "booking.com",
        "airbnb",
        "hotel",
    ],

    "Essen außer Haus": [
        "genuss & harmonie",
        "kantine",
        "restaurant",
        "lieferando",
        "mcdonald",
        "burger",
        "pizza",
        "eiscafe",
        "eiscafé",
        "cafe ",
        "café ",
    ],

    "Kleidung & Schuhe": [
        "adler modemärkte",
        "adler modemaerkte",
        "h&m",
        "h+m",
        "h+ m",
        "kik",
        "ernstings",
        "oellers schuhhaus",
        "schuhhaus",
    ],

    "Haushalt": [
        "nanu-nana",
        "nanu nana",
        "tedi",
        "action germany",
        "action",
    ],

    "Hobby & Freizeit": [
        "creativ shop",
        "nanu-nana",
        "nanu nana",
    ],

    "Shopping": [
        "amazon",
        "kleinanzeigen",
        "zalando",
        "ikea",
        "mediamarkt",
        "saturn",
    ],

    "Abos & Software": [
        "netflix",
        "spotify",
        "disney",
        "amazon prime",
        "google suno",
        "paypal *google suno",
        "suno",
    ],

    "Behörden & Abgaben": [
        "rhein-kreis neuss",
        "stadt korschenbroich",
        "kassenzeichen",
        "mahnungsnummer",
    ],

    "Rundfunkbeitrag": [
        "rundfunk ard",
        "rundfunkbeitrag",
        "ard, zdf",
        "ard zdf",
    ],

    "Glücksspiel": [
        "westdeutsche lotterie",
        "westlotto",
        "lotterie",
        "lotto",
    ],
}


def build_search_text(
    transaction: Transaction,
) -> str:
    """
    Kombiniert alle relevanten Textfelder.
    """

    return " ".join(
        [
            str(transaction.merchant or ""),
            str(transaction.transaction_type or ""),
            str(transaction.description or ""),
        ]
    ).lower()


def set_category(
    transaction: Transaction,
    category: str,
    subcategory: str,
    reason: str,
) -> Transaction:
    """
    Setzt eine regelbasierte Kategorie.
    """

    transaction.category = category
    transaction.subcategory = subcategory
    transaction.category_source = "rule"
    transaction.category_confidence = 1.0
    transaction.category_reason = reason

    return transaction


def categorize_transaction(
    transaction: Transaction,
) -> Transaction:

    normalized_type = transaction.normalized_type

    if normalized_type == "income":
        return set_category(
            transaction,
            "Einkommen",
            "Sonstiges Einkommen",
            "Einnahme anhand der Finanzregeln erkannt.",
        )

    if normalized_type == "refund":
        return set_category(
            transaction,
            "Rückerstattung",
            "Erstattung",
            "Rückerstattung anhand der Finanzregeln erkannt.",
        )

    if normalized_type == "savings":
        return set_category(
            transaction,
            "Sparen",
            "Spartransfer",
            "Spartransfer anhand der Finanzregeln erkannt.",
        )

    if normalized_type == "loan_payment":
        return set_category(
            transaction,
            "Hausdarlehen",
            "Darlehenszahlung",
            "Darlehenszahlung anhand des Verwendungszwecks erkannt.",
        )

    if normalized_type == "fee":
        return set_category(
            transaction,
            "Gebühren",
            "Bankgebühr",
            "Gebühr anhand des Transaktionstyps erkannt.",
        )

    if normalized_type == "transfer_in":
        return set_category(
            transaction,
            "Interner Transfer",
            "Transfer Eingang",
            "Interner Eingang anhand der Finanzregeln erkannt.",
        )

    if normalized_type == "transfer_out":
        return set_category(
            transaction,
            "Interner Transfer",
            "Transfer Ausgang",
            "Interner Ausgang anhand der Finanzregeln erkannt.",
        )

    if normalized_type == "unknown_inflow":
        return set_category(
            transaction,
            "Unbekannter Eingang",
            "Noch zu prüfen",
            "Herkunft des Eingangs konnte nicht sicher bestimmt werden.",
        )

    # -----------------------------------------------------
    # Normale Ausgaben
    # -----------------------------------------------------

    text = build_search_text(transaction)

    for category, keywords in CATEGORY_RULES.items():

        for keyword in keywords:

            if keyword in text:

                return set_category(
                    transaction,
                    category,
                    category,
                    f"Schlüsselwort-Regel erkannt: {keyword}",
                )

    # -----------------------------------------------------
    # Keine Regel gefunden
    # -----------------------------------------------------

    transaction.category = "Sonstiges"
    transaction.subcategory = "Noch zu prüfen"
    transaction.category_source = "unclassified"
    transaction.category_confidence = None
    transaction.category_reason = None

    return transaction