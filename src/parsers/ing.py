from __future__ import annotations

import re

from models import Transaction
from utils.money import parse_amount, AMOUNT_PATTERN
from parsers.base import lines


DATE_PATTERN = re.compile(r"^\d{2}\.\d{2}\.\d{4}$")


class INGParser:

    def parse(self, pages):

        transactions = []

        for page in pages:

            for block in page["blocks"]:

                block_lines = lines(block["text"])

                if len(block_lines) < 3:
                    continue

                # Eine ING-Buchung beginnt mit einem Datum
                if not DATE_PATTERN.match(block_lines[0]):
                    continue

                # Suche den Betrag
                amount_index = None

                for i, line in enumerate(block_lines):

                    if AMOUNT_PATTERN.fullmatch(line):
                        amount_index = i
                        break

                if amount_index is None:
                    continue

                # Für das ING-Format erwarten wir:
                #
                # Datum
                # Buchung + Empfänger
                # Betrag
                # Valuta
                # Verwendungszweck

                booking_date = block_lines[0]

                booking_line = block_lines[1]

                amount = parse_amount(
                    block_lines[amount_index]
                )

                value_date = None

                # Valuta steht nach dem Betrag normalerweise
                if amount_index + 1 < len(block_lines):
                    possible_date = block_lines[amount_index + 1]

                    if DATE_PATTERN.match(possible_date):
                        value_date = possible_date

                transaction_type, merchant = (
                    self.parse_booking_line(
                        booking_line
                    )
                )

                description_lines = block_lines[
                    amount_index + 2:
                ]

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

    def parse_booking_line(self, text):

        transaction_type = ""

        if text.startswith("Lastschrift"):
            transaction_type = "Lastschrift"

        elif text.startswith("Gutschrift/Dauerauftrag"):
            transaction_type = "Gutschrift/Dauerauftrag"

        elif text.startswith("Gutschrift"):
            transaction_type = "Gutschrift"

        elif text.startswith("Dauerauftrag"):
            transaction_type = "Dauerauftrag"

        elif text.startswith("Echtzeitüberweisung"):
            transaction_type = "Echtzeitüberweisung"

        elif text.startswith("Ueberweisung"):
            transaction_type = "Überweisung"

        elif text.startswith("Entgelt"):
            transaction_type = "Entgelt"

        # Der Händler steht normalerweise hinter dem Vorgang
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

                merchant = text[len(prefix):].strip()
                break

        return transaction_type, merchant