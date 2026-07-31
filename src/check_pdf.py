from pathlib import Path
import fitz

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PDF = PROJECT_ROOT / "data" / "pdf" / "Finanzreport_Nr._06_per_01.07.2026_A0A756.pdf"

doc = fitz.open(PDF)

print("Seiten:", len(doc))

for i, page in enumerate(doc):
    text = page.get_text()
    print(f"Seite {i+1}: {len(text)} Zeichen")