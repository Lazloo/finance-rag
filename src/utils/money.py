import re

AMOUNT_PATTERN = re.compile(
    r"[-+]\d{1,3}(?:\.\d{3})*,\d{2}"
)


def parse_amount(text: str) -> float:
    text = text.replace(".", "")
    text = text.replace(",", ".")

    return float(text)