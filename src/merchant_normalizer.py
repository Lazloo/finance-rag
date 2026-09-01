from __future__ import annotations

import re

from models import Transaction


# =========================================================
# Bekannte Händler-Aliase
# =========================================================
#
# Die Reihenfolge ist wichtig.
# Spezifische Treffer stehen weiter oben.
# =========================================================

MERCHANT_ALIASES = {
    # Bäckereien
    "baeckerei schneider": "Bäckerei Schneider",
    "bäckerei schneider": "Bäckerei Schneider",
    "stadtbaeckerei": "Stadtbäckerei",
    "stadtbäckerei": "Stadtbäckerei",
    "liefelder backhaus": "Liefelder Backhaus",
    "landbaeckerei stinges": "Landbäckerei Stinges",
    "landbäckerei stinges": "Landbäckerei Stinges",

    # Pänz & Piepmatz
    "paenz amp piepmatz": "Pänz & Piepmatz",
    "pänz & piepmatz": "Pänz & Piepmatz",
    "piepmatz": "Pänz & Piepmatz",

    # Lebensmittel
    "frischecenter": "Frischecenter",
    "edk*frischec raedle": "Frischecenter",
    "frischec raedle": "Frischecenter",
    "picnic": "Picnic",
    "lidl": "LIDL",
    "netto marken": "Netto",
    "meinaldi": "ALDI",
    "aldi": "ALDI",
    "trinkgut": "Trinkgut",

    # Drogerie
    "dm drogerie": "dm",
    "dm-drogerie": "dm",
    "drogeriemarkt": "dm",
    "rossmann": "ROSSMANN",

    # Mobilität
    "sb tanktreff": "SB Tanktreff",
    "deutsche tamoil": "Deutsche Tamoil",
    "shell deutschland": "Shell",
    "shell": "Shell",
    "auto service loehr": "Auto Service Loehr",

    # Kleidung
    "jeans fritz": "Jeans Fritz",
    "cecil": "CECIL",
    "nkd deutschland": "NKD",
    "nkd": "NKD",
    "h&m": "H&M",
    "ernstings": "Ernsting's",
    "kik": "KiK",
    "adler modemärkte": "Adler Modemärkte",
    "adler modemaerkte": "Adler Modemärkte",

    # Haushalt
    "hagebau": "hagebaumarkt",
    "tedi": "TEDi",
    "action germany": "Action",
    "nanu-nana": "Nanu-Nana",
    "nanu nana": "Nanu-Nana",

    # Kinder
    "smyths toys": "Smyths Toys",
    "buch und spielkiste": "Buch und Spielkiste",
    "glehner turnverein": "Glehner Turnverein",

    # Essen
    "genuss & harmonie": "Genuss & Harmonie",
    "brauhaus bernkastel": "Brauhaus Bernkastel",
    "eiscafe ciprian": "Eiscafe Ciprian",

    # Glücksspiel
    "westdeutsche lotterie": "Westdeutsche Lotterie",
    "westlotto": "Westlotto",

    # Telekommunikation
    "deutsche glasfaser": "Deutsche Glasfaser",

    # Behörden
    "rhein-kreis neuss": "Rhein-Kreis Neuss",
    "stadt korschenbroich": "Stadt Korschenbroich",

    # Rundfunk
    "rundfunk ard": "Rundfunkbeitrag",

    # Amazon
    "amazon payments europe": "Amazon",
    "amazon eu": "Amazon",
    "amazon digital germany": "Amazon",
}


def clean_text(text: str) -> str:
    """
    Bereinigt einen Händlertext grundsätzlich.
    """

    text = text.strip()

    # Häufige Karten-/Zahlungspräfixe entfernen
    prefixes = [
        "VISA ",
        "Visa ",
        "SUMUP *",
        "SumUp *",
        "PAYPAL *",
        "PayPal *",
    ]

    changed = True

    while changed:

        changed = False

        for prefix in prefixes:

            if text.startswith(prefix):
                text = text[len(prefix):].strip()
                changed = True

    # Comdirect-Karteninformationen entfernen
    text = re.sub(
        r"\s*Karte Nr\..*$",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"\s*Kartenzahlung.*$",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # Datum am Ende entfernen
    text = re.sub(
        r"\s*\d{4}-\d{2}-\d{2}.*$",
        "",
        text,
    )

    # Mehrfache Leerzeichen zusammenfassen
    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def normalize_merchant(
    transaction: Transaction,
) -> Transaction:
    """
    Erzeugt einen einheitlichen Händlernamen.

    Die originale merchant-Angabe bleibt unverändert.
    """

    merchant = transaction.merchant or ""
    description = transaction.description or ""

    combined = (
        f"{merchant} {description}"
    ).lower()

    # -----------------------------------------------------
    # Spezielle Fälle zuerst
    # -----------------------------------------------------

    for search_term, normalized_name in MERCHANT_ALIASES.items():

        if search_term in combined:
            transaction.merchant_normalized = normalized_name
            return transaction

    # -----------------------------------------------------
    # Falls der Merchant nur ein Zahlungsdienstleister ist,
    # versuchen wir den tatsächlichen Händler aus der
    # Beschreibung zu extrahieren.
    # -----------------------------------------------------

    payment_processors = [
        "nexi germany gmbh",
        "unzer e-com gmbh",
        "sumup",
    ]

    merchant_lower = merchant.lower()

    if any(
        processor in merchant_lower
        for processor in payment_processors
    ):

        cleaned_description = clean_text(
            description
        )

        if cleaned_description:
            transaction.merchant_normalized = (
                cleaned_description
            )
            return transaction

    # -----------------------------------------------------
    # Allgemeine Bereinigung
    # -----------------------------------------------------

    cleaned = clean_text(
        merchant
    )

    if cleaned:
        transaction.merchant_normalized = cleaned
    else:
        transaction.merchant_normalized = (
            "Unbekannter Händler"
        )

    return transaction