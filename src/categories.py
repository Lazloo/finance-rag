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


def categorize_transaction(
    transaction: Transaction,
) -> Transaction:
    """
    Weist einer Transaktion eine Kategorie zu.
    """

    normalized_type = transaction.normalized_type

    # =====================================================
    # Finanzielle Kategorien
    # =====================================================

    if normalized_type == "income":
        transaction.category = "Einkommen"
        transaction.subcategory = "Sonstiges Einkommen"
        return transaction

    if normalized_type == "refund":
        transaction.category = "Rückerstattung"
        transaction.subcategory = "Erstattung"
        return transaction

    if normalized_type == "savings":
        transaction.category = "Sparen"
        transaction.subcategory = "Spartransfer"
        return transaction

    if normalized_type == "loan_payment":
        transaction.category = "Hausdarlehen"
        transaction.subcategory = "Darlehenszahlung"
        return transaction

    if normalized_type == "fee":
        transaction.category = "Gebühren"
        transaction.subcategory = "Bankgebühr"
        return transaction

    if normalized_type == "transfer_in":
        transaction.category = "Interner Transfer"
        transaction.subcategory = "Transfer Eingang"
        return transaction

    if normalized_type == "transfer_out":
        transaction.category = "Interner Transfer"
        transaction.subcategory = "Transfer Ausgang"
        return transaction

    if normalized_type == "unknown_inflow":
        transaction.category = "Unbekannter Eingang"
        transaction.subcategory = "Noch zu prüfen"
        return transaction

    # =====================================================
    # Normale Ausgaben
    # =====================================================

    text = build_search_text(transaction)

    for category, keywords in CATEGORY_RULES.items():

        for keyword in keywords:

            if keyword in text:

                transaction.category = category
                transaction.subcategory = category

                return transaction

    # =====================================================
    # Noch nicht erkannt
    # =====================================================

    transaction.category = "Sonstiges"
    transaction.subcategory = "Noch zu prüfen"

    return transaction