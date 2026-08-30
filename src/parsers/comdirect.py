from __future__ import annotations

import re

from models import Transaction
from parsers.base import lines
from utils.money import parse_amount, AMOUNT_PATTERN


DATE_PATTERN = re.compile(r"^\d{2}\.\d{2}\.\d{4}$")


class ComdirectParser:
    def is_transaction_start(self, block_lines: list[str]) -> bool:
        """
        Ein echter Comdirect-Transaktionsheader enthält normalerweise:
        Datum
        Valuta
        Transaktionstyp
        """

        if len(block_lines) < 3:
            return False

        # Erste beiden Zeilen müssen Datum sein
        if not DATE_PATTERN.match(block_lines[0]):
            return False

        if not DATE_PATTERN.match(block_lines[1]):
            return False

        third_line = " ".join(
            block_lines[2:]
        ).lower()

        transaction_keywords = [
            "lastschrift",
            "kartenverfügung",
            "überweisung",
            "gutschrift",
            "devisen",
            "echtzeitüberweisung",
        ]

        return any(
            keyword in third_line
            for keyword in transaction_keywords
        )
    
    def parse(self, pages):

        blocks = []

        for page in pages:
            blocks.extend(page["blocks"])

        transactions = []

        i = 0

        while i < len(blocks):

            block_text = blocks[i]["text"]
            block_lines = lines(block_text)

            # Kopfzeilen / Tabellenüberschrift
            if "Buchungstag" in block_text:
                i += 1
                continue

            # Alter Saldo ist keine Transaktion
            if block_text.startswith("Alter Saldo"):
                i += 1
                continue

            # Eine Transaktion beginnt mit einem Datum
            if not self.is_transaction_start(block_lines):
                i += 1
                continue

            start = i
            end = i + 1

            # Bis zum nächsten Datumsblock laufen
            while end < len(blocks):

                next_lines = lines(blocks[end]["text"])

                if next_lines and DATE_PATTERN.match(next_lines[0]):
                    break

                end += 1

            transaction_blocks = blocks[start:end]

            transaction = self.parse_transaction(
                transaction_blocks
            )

            if transaction is not None:
                transactions.append(transaction)

            i = end

        return transactions

    def parse_transaction(self, transaction_blocks):

        if not transaction_blocks:
            return None

        header_lines = lines(
            transaction_blocks[0]["text"]
        )

        if not self.is_transaction_start(header_lines):
            return None

        if not header_lines:
            return None

        booking_date = header_lines[0]

        value_date = None

        if (
            len(header_lines) > 1
            and DATE_PATTERN.match(header_lines[1])
        ):
            value_date = header_lines[1]

        transaction_type = self.detect_transaction_type(
            transaction_blocks
        )

        # Betrag suchen
        amount = None

        for block in reversed(transaction_blocks):

            for line in reversed(lines(block["text"])):

                if AMOUNT_PATTERN.fullmatch(line):

                    amount = parse_amount(line)
                    break

            if amount is not None:
                break

        if amount is None:
            return None

        merchant = self.extract_merchant(
            transaction_blocks,
            transaction_type,
        )

        description = self.extract_description(
            transaction_blocks,
            transaction_type,
        )

        return Transaction(
            bank="comdirect",
            booking_date=booking_date,
            value_date=value_date,
            transaction_type=transaction_type,
            merchant=merchant,
            amount=amount,
            description=description,
        )

    def detect_transaction_type(
        self,
        transaction_blocks,
    ):

        text = "\n".join(
            block["text"]
            for block in transaction_blocks
        ).lower()

        if "lastschrift" in text:
            return "Lastschrift"

        if "kartenverfügung" in text:
            return "Kartenverfügung"

        if "echtzeitüberweisung" in text:
            return "Echtzeitüberweisung"

        if "überweisung" in text:
            return "Überweisung"

        if "dauerauftrag" in text:
            return "Dauerauftrag"

        if "gutschrift" in text:
            return "Gutschrift"

        if "devisen" in text:
            return "Devisen"

        return "Unbekannt"

    def extract_merchant(
        self,
        transaction_blocks,
        transaction_type,
    ):

        if transaction_type == "Devisen":

            if len(transaction_blocks) > 1:

                candidate = " ".join(
                    lines(
                        transaction_blocks[1]["text"]
                    )
                )

                if candidate:
                    return candidate

            return "Devisen"

        # Bei den normalen Buchungen steht der
        # Auftraggeber/Empfänger im Block nach dem Header.
        if len(transaction_blocks) > 1:

            candidate = " ".join(
                lines(transaction_blocks[1]["text"])
            )

            if candidate:
                return candidate

        return "Unbekannt"

    def extract_description(
        self,
        transaction_blocks,
        transaction_type,
    ):

        if len(transaction_blocks) <= 1:
            return ""

        description_parts = []

        for block in transaction_blocks[2:]:

            text = " ".join(
                lines(block["text"])
            )

            if not text:
                continue

            # Betrag nicht erneut in die Beschreibung übernehmen
            if AMOUNT_PATTERN.fullmatch(text):
                continue

            description_parts.append(text)

        return " ".join(description_parts)