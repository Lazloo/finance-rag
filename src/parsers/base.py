import re

DATE_PATTERN = re.compile(
    r"\d{2}\.\d{2}\.\d{4}"
)


def is_date(text: str) -> bool:
    return bool(
        DATE_PATTERN.match(text)
    )


def first_line(text: str) -> str:
    return text.splitlines()[0].strip()


def lines(text: str):
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]