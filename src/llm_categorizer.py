from __future__ import annotations

import json

import ollama

from models import Transaction


LLM_MODEL = "qwen2.5:3b"


CATEGORIES = [
    "Lebensmittel",
    "Drogerie",
    "Gesundheit",
    "Kinder",
    "Mobilität",
    "Wohnen",
    "Telekommunikation",
    "Reisen",
    "Essen außer Haus",
    "Kleidung & Schuhe",
    "Haushalt",
    "Hobby & Freizeit",
    "Shopping",
    "Abos & Software",
    "Behörden & Abgaben",
    "Rundfunkbeitrag",
    "Glücksspiel",
    "Sonstiges",
]


def classify_with_ollama(
    transaction: Transaction,
) -> dict:
    """
    Klassifiziert eine unbekannte Transaktion mit Ollama.
    """

    prompt = f"""
Du bist ein Assistent zur Klassifizierung privater
Kontobewegungen.

Analysiere die folgende Transaktion.

Händler:
{transaction.merchant}

Transaktionstyp:
{transaction.transaction_type}

Betrag:
{transaction.amount:.2f} EUR

Verwendungszweck:
{transaction.description or "Nicht vorhanden"}

Erlaubte Kategorien:
{json.dumps(CATEGORIES, ensure_ascii=False)}

Regeln:

1. Wähle genau eine Kategorie aus der Liste.
2. Erfinde keinen Händler.
3. Verwende "Sonstiges", wenn die vorhandenen Daten keine
   zuverlässige Zuordnung erlauben.
4. confidence muss zwischen 0 und 1 liegen.
5. confidence beschreibt deine Sicherheit bezüglich der Kategorie.
6. Antworte ausschließlich als JSON.

Erwartetes Format:

{{
  "category": "Lebensmittel",
  "subcategory": "Beispiel",
  "confidence": 0.85,
  "reason": "Kurze Begründung"
}}
"""

    response = ollama.chat(
        model=LLM_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        format="json",
    )

    content = response["message"]["content"]

    result = json.loads(content)

    return result


def apply_llm_category(
    transaction: Transaction,
) -> Transaction:
    """
    Klassifiziert eine Transaktion mit Ollama.

    Bei geringer Sicherheit bleibt die Kategorie Sonstiges.
    """

    result = classify_with_ollama(
        transaction
    )

    category = result.get(
        "category",
        "Sonstiges",
    )

    subcategory = result.get(
        "subcategory",
        "",
    )

    confidence = float(
        result.get(
            "confidence",
            0.0,
        )
    )

    reason = result.get(
        "reason",
        "",
    )

    # Sicherheit auf gültigen Bereich begrenzen
    confidence = max(
        0.0,
        min(1.0, confidence),
    )

    # Nur erlaubte Kategorien akzeptieren
    if category not in CATEGORIES:
        category = "Sonstiges"

    transaction.category_source = "ollama"
    transaction.category_confidence = confidence
    transaction.category_reason = reason

    # Unterhalb dieser Schwelle keine automatische
    # Umklassifizierung.
    if confidence >= 0.75:
        transaction.category = category
        transaction.subcategory = (
            subcategory or "KI-Klassifizierung"
        )
    else:
        transaction.category = "Sonstiges"
        transaction.subcategory = "Manuelle Prüfung"

    return transaction


if __name__ == "__main__":
    print("Ollama-Kategorisierer bereit.")
    print(f"Modell: {LLM_MODEL}")