from pathlib import Path

import fitz

from parsers.comdirect import ComdirectParser
from parsers.ing import INGParser


class BankDispatcher:

    def detect_bank(self, pdf_file: Path) -> str:
        """
        Erkennt die Bank anhand des PDF-Inhalts.
        """

        with fitz.open(pdf_file) as doc:

            # Nur die ersten Seiten reichen für die Erkennung.
            text_parts = []

            for page in doc[:3]:
                text_parts.append(page.get_text())

            text = "\n".join(text_parts).lower()

        if "comdirect" in text or "finanzreport" in text:
            return "comdirect"

        if "ing-diba" in text or "ing-diba ag" in text or "ing.de" in text:
            return "ing"

        raise ValueError(
            f"Bank konnte nicht erkannt werden: {pdf_file.name}"
        )

    def create_parser(self, bank: str):

        if bank == "comdirect":
            return ComdirectParser()

        if bank == "ing":
            return INGParser()

        raise ValueError(f"Unbekannte Bank: {bank}")

    def parse(self, pdf_file: Path, pages):

        bank = self.detect_bank(pdf_file)

        parser = self.create_parser(bank)

        transactions = parser.parse(pages)

        return bank, transactions