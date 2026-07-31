from pathlib import Path
import pdfplumber

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PDF = PROJECT_ROOT / "data" / "pdf" / "Finanzreport_Nr._06_per_01.07.2026_A0A756.pdf"

with pdfplumber.open(PDF) as pdf:

    page = pdf.pages[1]      # zweite Seite

    words = page.extract_words(
        keep_blank_chars=False,
        use_text_flow=True
    )

    print(f"{len(words)} Wörter\n")

    for word in words[:80]:
        print(word)