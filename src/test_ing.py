from pathlib import Path

from pdf.extractor import extract_blocks
from parsers.ing import INGParser


pdf = Path(
    "data/pdf/Girokonto_5421708039_Kontoauszug_20260702.pdf"
)

pages = extract_blocks(pdf)

parser = INGParser()

transactions = parser.parse(pages)

print(
    f"{len(transactions)} Transaktionen gefunden\n"
)

for transaction in transactions[:20]:

    print("-" * 70)

    print("Datum :", transaction.booking_date)
    print("Typ   :", transaction.transaction_type)
    print("Firma :", transaction.merchant)
    print("Betrag:", transaction.amount)
    print("Text  :", transaction.description)