from pathlib import Path

from pdf.extractor import extract_blocks


pdf = Path(
    "data/pdf/Girokonto_5421708039_Kontoauszug_20260702.pdf"
)

pages = extract_blocks(pdf)

for page_number, page in enumerate(pages, start=1):

    for block_number, block in enumerate(page["blocks"]):

        text = block["text"]

        if (
            "1.860,00" in text
            or "2.370,00" in text
            or "Gutschrift yyyyy" in text
            or "Gutschrift/Dauerauftrag" in text
        ):
            print("=" * 100)
            print(f"Seite: {page_number}")
            print(f"Block: {block_number}")
            print(text)