from pathlib import Path

from pdf.extractor import extract_blocks
from parsers.dispatcher import BankDispatcher


dispatcher = BankDispatcher()

pdf_files = sorted(Path("data/pdf").glob("*.pdf"))

for pdf in pdf_files:

    print("=" * 70)
    print(f"PDF: {pdf.name}")

    pages = extract_blocks(pdf)

    bank, transactions = dispatcher.parse(pdf, pages)

    print(f"Bank: {bank}")
    print(f"Transaktionen: {len(transactions)}")

    for transaction in transactions[:3]:
        print(
            f"  {transaction.booking_date} | "
            f"{transaction.merchant} | "
            f"{transaction.amount:.2f}"
        )