from pathlib import Path
import fitz


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PDF_DIR = PROJECT_ROOT / "data" / "pdf"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"


def extract_pdf_text(pdf_path: Path) -> str:
    """Extrahiert den kompletten Text einer PDF."""

    text = []

    with fitz.open(pdf_path) as doc:
        for page in doc:
            page_text = page.get_text("text")
            text.append(page_text)

    return "\n".join(text)


def save_text(text: str, pdf_path: Path):
    """Speichert den extrahierten Text."""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_file = OUTPUT_DIR / f"{pdf_path.stem}.txt"

    output_file.write_text(text, encoding="utf-8")

    print(f"✓ Gespeichert: {output_file.name}")


def process_pdf(pdf_path: Path):

    print(f"Lese: {pdf_path.name}")

    text = extract_pdf_text(pdf_path)

    print(f"  Zeichen: {len(text)}")

    save_text(text, pdf_path)


def main():

    if not PDF_DIR.exists():
        print("Ordner data/pdf existiert nicht.")
        return

    pdfs = sorted(PDF_DIR.glob("*.pdf"))

    if not pdfs:
        print("Keine PDFs gefunden.")
        return

    print(f"{len(pdfs)} PDF(s) gefunden.\n")

    for pdf in pdfs:
        process_pdf(pdf)

    print("\nFertig.")


if __name__ == "__main__":
    main()