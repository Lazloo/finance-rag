from __future__ import annotations

import re


TECHNICAL_PATTERNS = [
    r"End-to-End-Ref\.:.*",
    r"Referenz:.*",
    r"Mandat:.*",
    r"Gläubiger-ID:.*",
    r"Glaeubiger-ID:.*",
    r"Folgenr\..*",
    r"Verfalld\..*",
    r"Karte Nr\..*",
    r"Kartenzahlung.*",
]


def clean_transaction_text(text: str) -> str:
    """
    Entfernt technische Bankinformationen aus einem Text.
    """

    result = text or ""

    for pattern in TECHNICAL_PATTERNS:

        result = re.sub(
            pattern,
            " ",
            result,
            flags=re.IGNORECASE,
        )

    # Mehrfache Leerzeichen entfernen
    result = re.sub(
        r"\s+",
        " ",
        result,
    )

    return result.strip()