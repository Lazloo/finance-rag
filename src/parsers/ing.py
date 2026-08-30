from __future__ import annotations

import re

from models import Transaction
from parsers.base import lines
from utils.money import parse_amount, AMOUNT_PATTERN


DATE_PATTERN = re.compile(
    r"^\d{2}\.\d{2}\.\d{4}$"
)


class INGParser:

    def parse(self, pages):

        transactions = []

        for page in pages:

            for block in page["blocks"]:

                block_lines = lines(
                    block["text"]
                )

                # Eine ING-Buchung benötigt mindestens:
                #
                # 1. Buchungsdatum
                # 2. Buchung / Empfänger
                # 3. Betrag

                if len(block_lines) < 3:
                    continue

                # Erste Zeile muss Datum sein
                if not DATE_PATTERN.match(
                    block_lines[0]
                ):
                    continue

                # -------------------------------------------------
                # Betrag muss die dritte Zeile sein
                # -------------------------------------------------

                amount_text = block_lines[2]

                if not AMOUNT_PATTERN.fullmatch(
                    amount_text
                ):
                    continue

                booking_date = block_lines[0]

                booking_line = block_lines[1]

                amount = parse_amount(
                    amount_text
                )

                # -------------------------------------------------
                # Valuta
                # -------------------------------------------------

                value_date = None

                if (
                    len(block_lines) > 3
                    and DATE_PATTERN.match(
                        block_lines[3]
                    )
                ):
                    value_date = block_lines[3]

                # -------------------------------------------------
                # Transaktionstyp / Händler
                # -------------------------------------------------

                transaction_type, merchant = (
                    self.parse_booking_line(
                        booking_line
                    )
                )

                # -------------------------------------------------
                # Verwendungszweck
                # -------------------------------------------------

                description_lines = block_lines[4:]

                description = " ".join(
                    description_lines
                )

                transactions.append(
                    Transaction(
                        bank="ING",
                        booking_date=booking_date,
                        value_date=value_date,
                        transaction_type=transaction_type,
                        merchant=merchant,
                        amount=amount,
                        description=description,
                    )
                )

        return transactions

    def parse_booking_line(
        self,
        text: str,
    ):

        transaction_type = ""

        if text.startswith("Lastschrift"):
            transaction_type = "Lastschrift"

        elif text.startswith(
            "Gutschrift/Dauerauftrag"
        ):
            transaction_type = (
                "Gutschrift/Dauerauftrag"
            )

        elif text.startswith("Gutschrift"):
            transaction_type = "Gutschrift"

        elif text.startswith(
            "Dauerauftrag/Terminueberw."
        ):
            transaction_type = "Dauerauftrag"

        elif text.startswith("Dauerauftrag"):
            transaction_type = "Dauerauftrag"

        elif text.startswith(
            "Echtzeitüberweisung"
        ):
            transaction_type = (
                "Echtzeitüberweisung"
            )

        elif text.startswith("Ueberweisung"):
            transaction_type = "Überweisung"

        elif text.startswith("Entgelt"):
            transaction_type = "Entgelt"

        merchant = text

        prefixes = [
            "Lastschrift ",
            "Gutschrift/Dauerauftrag ",
            "Gutschrift ",
            "Dauerauftrag/Terminueberw. ",
            "Dauerauftrag ",
            "Echtzeitüberweisung ",
            "Ueberweisung ",
            "Entgelt ",
        ]

        for prefix in prefixes:

            if text.startswith(prefix):

                merchant = (
                    text[len(prefix):]
                    .strip()
                )

                break

        return transaction_type, merchant