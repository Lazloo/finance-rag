from pathlib import Path

from pdf.extractor import extract_blocks


pdf = Path(
    "data/pdf/Girokonto_5421708039_Kontoauszug_20260702.pdf"
)

pages = extract_blocks(pdf)

for page_number, page in enumerate(pages, start=1):
    print(f"\n{'#' * 30}")
    print(f"SEITE {page_number}")
    print(f"{'#' * 30}")

    for i, block in enumerate(page["blocks"][:30]):
        print("=" * 70)
        print(i)
        print(block["text"])