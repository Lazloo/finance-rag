from pathlib import Path

from pdf.extractor import extract_blocks


pdf = Path(
    "data/pdf/Finanzreport_Nr._06_per_01.07.2026_A0A756.pdf"
)


pages = extract_blocks(pdf)


for block in pages[1]["blocks"][:15]:
    print(block)