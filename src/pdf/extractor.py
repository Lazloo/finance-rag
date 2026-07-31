from pathlib import Path
import fitz


def extract_blocks(pdf_file: Path):

    doc = fitz.open(pdf_file)

    pages = []

    for page_number, page in enumerate(doc, start=1):

        blocks = page.get_text("blocks")

        page_blocks = []

        for block in blocks:

            text = block[4].strip()

            if not text:
                continue

            page_blocks.append(
                {
                    "x": block[0],
                    "y": block[1],
                    "text": text
                }
            )

        pages.append(
            {
                "page": page_number,
                "blocks": page_blocks
            }
        )

    return pages