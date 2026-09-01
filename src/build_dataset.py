from pathlib import Path
from llm_categorizer import apply_llm_category
from categories import categorize_transaction
from exporter import export_json
from parsers.dispatcher import BankDispatcher
from pdf.extractor import extract_blocks
from transaction_rules import normalize_transaction
from merchant_normalizer import normalize_merchant


PDF_DIR = Path("data/pdf")

OUTPUT_FILE = Path(
    "data/processed/transactions.json"
)


def main():
    dispatcher = BankDispatcher()

    all_transactions = []

    pdf_files = sorted(
        PDF_DIR.glob("*.pdf")
    )

    if not pdf_files:
        print("Keine PDFs gefunden.")
        return

    print(
        f"{len(pdf_files)} PDF-Dateien gefunden.\n"
    )

    for pdf_file in pdf_files:

        print("=" * 70)
        print(pdf_file.name)

        try:
            # -------------------------------------------------
            # PDF extrahieren
            # -------------------------------------------------

            pages = extract_blocks(
                pdf_file
            )

            # -------------------------------------------------
            # Bank erkennen und Parser ausführen
            # -------------------------------------------------

            bank, transactions = dispatcher.parse(
                pdf_file,
                pages,
            )

            print(
                f"Bank: {bank}"
            )

            print(
                f"Transaktionen gefunden: "
                f"{len(transactions)}"
            )

            # -------------------------------------------------
            # Finanzielle Bedeutung bestimmen
            # -------------------------------------------------

            transactions = [
                normalize_transaction(transaction)
                for transaction in transactions
            ]

            transactions = [
                normalize_merchant(transaction)
                for transaction in transactions
            ]

            transactions = [
                categorize_transaction(transaction)
                for transaction in transactions
            ]

            # -------------------------------------------------
            # Kategorie bestimmen
            # -------------------------------------------------

            # transactions = [
            #     categorize_transaction(transaction)
            #     for transaction in transactions
            # ]

            # # -------------------------------------------------
            # # Unbekannte Ausgaben durch Ollama klassifizieren
            # # -------------------------------------------------

            # for transaction in transactions:

            #     if (
            #         transaction.normalized_type == "expense"
            #         and transaction.category == "Sonstiges"
            #     ):
            #         print(
            #             f"Ollama analysiert: "
            #             f"{transaction.merchant}"
            #         )

            #         try:
            #             apply_llm_category(
            #                 transaction
            #             )

            #         except Exception as exc:
            #             print(
            #                 f"Ollama-Fehler bei "
            #                 f"{transaction.merchant}: "
            #                 f"{exc}"
            #             )

            #             transaction.category_source = "ollama"
            #             transaction.category_confidence = 0.0
            #             transaction.category_reason = (
            #                 f"Fehler bei Ollama: {exc}"
            #             )

            # # -------------------------------------------------
            # # Zur Gesamtliste hinzufügen
            # # -------------------------------------------------

            all_transactions.extend(
                transactions
            )

        except Exception as exc:

            print(
                f"FEHLER bei {pdf_file.name}:"
            )
            print(
                f"  {type(exc).__name__}: {exc}"
            )

    # ---------------------------------------------------------
    # Gesamtergebnis
    # ---------------------------------------------------------

    print()
    print("=" * 70)

    print(
        f"Gesamt: "
        f"{len(all_transactions)} "
        f"Transaktionen"
    )

    # ---------------------------------------------------------
    # JSON speichern
    # ---------------------------------------------------------

    export_json(
        all_transactions,
        OUTPUT_FILE,
    )


if __name__ == "__main__":
    main()