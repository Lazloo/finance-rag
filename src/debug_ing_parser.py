from pathlib import Path

from pdf.extractor import extract_blocks
from parsers.ing import INGParser


pdf = Path(
    "data/pdf/Girokonto_5421708039_Kontoauszug_20260702.pdf"
)

pages = extract_blocks(pdf)

parser = INGParser()

transactions = parser.parse(pages)

print("=" * 80)
print("PARSED TRANSACTIONS: 1.860 / 2.370")
print("=" * 80)

for transaction in transactions:

    if abs(transaction.amount - 1860.00) < 0.01:
        print("\n1.860 € GEFUNDEN")
        print(transaction)

    if abs(transaction.amount - 2370.00) < 0.01:
        print("\n2.370 € GEFUNDEN")
        print(transaction)