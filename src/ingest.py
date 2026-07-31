from pathlib import Path
import pdfplumber
import json

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PDF_DIR = PROJECT_ROOT / "data" / "pdf"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"


def extract_pdf(pdf_file: Path):

    pages = []

    with pdfplumber.open(pdf_file) as pdf:

        print(f"{pdf_file.name}: {len(pdf.pages)} Seiten")

        for page_number, page in enumerate(pdf.pages, start=1):

            text = page.extract_text() or ""

            tables = page.extract_tables()

            pages.append(
                {
                    "page": page_number,
                    "text": text,
                    "tables": tables,
                }
            )

    return pages


def save_json(pdf_file: Path, pages):

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_file = OUTPUT_DIR / f"{pdf_file.stem}.json"

    with open(output_file, "w", encoding="utf-8") as f:

        json.dump(
            pages,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print(f"Gespeichert: {output_file}")


def main():

    pdfs = sorted(PDF_DIR.glob("*.pdf"))

    if not pdfs:
        print("Keine PDFs gefunden.")
        return

    for pdf in pdfs:

        pages = extract_pdf(pdf)

        save_json(pdf, pages)


if __name__ == "__main__":
    main()