from pathlib import Path
import csv

from models import Transaction


def export_csv(transactions: list[Transaction], filename: Path):

    filename.parent.mkdir(parents=True, exist_ok=True)

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.writer(f)

        writer.writerow(
            [
                "bank",
                "booking_date",
                "value_date",
                "transaction_type",
                "merchant",
                "amount",
                "description",
            ]
        )

        for t in transactions:

            writer.writerow(
                [
                    t.bank,
                    t.booking_date,
                    t.value_date,
                    t.transaction_type,
                    t.merchant,
                    t.amount,
                    t.description.replace("\n", " "),
                ]
            )