from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from models import Transaction


def export_json(
    transactions: list[Transaction],
    filename: Path,
) -> None:
    """
    Speichert Transaktionen als JSON.
    """

    filename.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = [
        asdict(transaction)
        for transaction in transactions
    ]

    filename.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        f"{len(transactions)} Transaktionen gespeichert: "
        f"{filename}"
    )