from pathlib import Path

from pdf.extractor import extract_blocks
from parsers.comdirect import ComdirectParser
from exporter import export_csv

pdf = Path(
    "data/pdf/Finanzreport_Nr._06_per_01.07.2026_A0A756.pdf"
)

pages = extract_blocks(pdf)

parser = ComdirectParser()

transactions = parser.parse(pages)

print(f"{len(transactions)} Transaktionen\n")

for t in transactions[:10]:

    print("-" * 70)
    print("Datum :", t.booking_date)
    print("Typ   :", t.transaction_type)
    print("Firma :", t.merchant)
    print("Betrag:", t.amount)

    

export_csv(
    transactions,
    Path("database/comdirect.csv")
)

print()

print("CSV geschrieben.")