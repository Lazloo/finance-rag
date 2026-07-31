from __future__ import annotations

import re

from models import Transaction
from parsers.base import lines
from utils.money import parse_amount, AMOUNT_PATTERN


DATE_PATTERN = re.compile(r"\d{2}\.\d{2}\.\d{4}")


class ComdirectParser:

    def parse(self, pages):

        blocks = []

        # Alle Seiten hintereinander sammeln
        for page in pages:
            blocks.extend(page["blocks"])

        transactions = []

        i = 0

        while i < len(blocks):

            block = blocks[i]["text"]

            # Header überspringen
            if "Buchungstag" in block:
                i += 1
                continue

            # Alter Saldo überspringen
            if block.startswith("Alter Saldo"):
                i += 1
                continue

            block_lines = lines(block)

            if not block_lines:
                i += 1
                continue

            # Beginnt der Block mit einem Datum?
            if not DATE_PATTERN.match(block_lines[0]):
                i += 1
                continue

            # Wir benötigen mindestens 4 Blöcke
            if i + 3 >= len(blocks):
                break

            header = blocks[i]["text"]
            merchant = blocks[i + 1]["text"]
            description = blocks[i + 2]["text"]
            amount = blocks[i + 3]["text"]

            if not AMOUNT_PATTERN.fullmatch(amount.strip()):
                i += 1
                continue

            transactions.append(
                self.build_transaction(
                    header,
                    merchant,
                    description,
                    amount,
                )
            )

            i += 4

        return transactions

    def build_transaction(
        self,
        header,
        merchant,
        description,
        amount,
    ):

        header_lines = lines(header)

        booking_date = header_lines[0]

        value_date = None

        if len(header_lines) > 1:
            if DATE_PATTERN.match(header_lines[1]):
                value_date = header_lines[1]

        transaction_type = ""

        for line in header_lines:

            if "Lastschrift" in line:
                transaction_type = "Lastschrift"

            elif "Kartenverfügung" in line:
                transaction_type = "Kartenverfügung"

            elif "Überweisung" in line:
                transaction_type = "Überweisung"

            elif "Gutschrift" in line:
                transaction_type = "Gutschrift"

        return Transaction(
            bank="comdirect",
            booking_date=booking_date,
            value_date=value_date,
            transaction_type=transaction_type,
            merchant=" ".join(lines(merchant)),
            amount=parse_amount(amount),
            description=description,
        )