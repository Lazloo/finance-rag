import re


AMOUNT_PATTERN = re.compile(
    r"[-+]?\d{1,3}(?:\.\d{3})*,\d{2}"
)


def parse_amount(text: str) -> float:
    """
    Wandelt deutsche Geldbeträge in float um.

    Beispiele:
        -160,00   -> -160.0
        1.860,00  -> 1860.0
        +4.595,11 -> 4595.11
    """

    value = text.strip()

    value = value.replace(".", "")
    value = value.replace(",", ".")

    return float(value)