from __future__ import annotations

import json

import ollama

from text_cleaner import clean_transaction_text
from vector_store import hybrid_search


LLM_MODEL = "qwen2.5:7b"


CATEGORIES = [
    "Lebensmittel",
    "Shopping",
    "Telekommunikation",
    "Sonstiges",
    "Drogerie",
    "Kinder",
    "Glücksspiel",
    "Mobilität",
    "Wohnen",
    "Gesundheit",
    "Haushalt",
    "Kleidung & Schuhe",
    "Essen außer Haus",
    "Abos & Software",
    "Behörden & Abgaben",
    "Hobby & Freizeit",
    "Reisen",
    "Rundfunkbeitrag",
]


def build_transaction_text(transaction: dict) -> str:
    merchant = (
        transaction.get("merchant_normalized")
        or transaction.get("merchant")
        or ""
    )

    description = clean_transaction_text(
        transaction.get("description", "")
    )

    amount = transaction.get("amount", 0)

    return (
        f"Händler: {merchant}\n"
        f"Verwendungszweck: {description}\n"
        f"Betrag: {amount:.2f} EUR"
    )


def build_rag_context(results: dict) -> str:
    lines = []

    exact_matches = results.get("exact", [])
    semantic_matches = results.get("semantic", [])

    if exact_matches:
        lines.append(
            "Historische Transaktionen desselben Händlers:"
        )

        for match in exact_matches[:8]:
            lines.append(
                "- "
                f"{match.get('merchant')} | "
                f"{match.get('category')} | "
                f"{match.get('subcategory') or ''} | "
                f"{match.get('amount', 0):.2f} EUR"
            )

        return "\n".join(lines)

    if semantic_matches:
        relevant_matches = [
            match
            for match in semantic_matches
            if match.get("distance", 999) <= 0.50
        ]

        if not relevant_matches:
            return (
                "Keine ausreichend ähnlichen historischen "
                "Transaktionen gefunden."
            )

        lines.append(
            "Semantisch ähnliche historische Transaktionen:"
        )

        for match in relevant_matches[:6]:
            lines.append(
                "- "
                f"{match.get('merchant')} | "
                f"{match.get('category')} | "
                f"{match.get('subcategory') or ''} | "
                f"Distanz: {match.get('distance', 0):.4f}"
            )

        return "\n".join(lines)

    return (
        "Keine passenden historischen Transaktionen "
        "gefunden."
    )


def build_prompt(
    transaction: dict,
    rag_context: str,
) -> str:
    transaction_text = build_transaction_text(
        transaction
    )

    categories_text = "\n".join(
        f"- {category}"
        for category in CATEGORIES
    )

    return f"""
Du kategorisierst private Banktransaktionen.

Ordne die folgende Ausgabe genau EINER Kategorie zu.

Mögliche Kategorien:
{categories_text}

WICHTIGE REGELN:

1. Analysiere zuerst Händler und Verwendungszweck der aktuellen
   Transaktion.

2. Der Verwendungszweck ist besonders wichtig.
   Er kann den tatsächlichen Geschäftszweck des Händlers
   enthalten, auch wenn der Händlername nur ein Zahlungsdienstleister
   oder ein technischer Name ist.

3. Historische Transaktionen dienen nur als zusätzlicher Kontext.
   Übernimm deren Kategorie NICHT automatisch.

4. Wenn historische Beispiele nicht zur aktuellen Transaktion
   passen, ignoriere sie.

5. Erfinde keine Informationen und keine Händleraktivitäten.

6. Wenn die aktuelle Transaktion aufgrund ihres Händlers oder
   Verwendungszwecks ausreichend eindeutig ist, kategorisiere sie
   direkt.

7. Verwende "Sonstiges" nur dann, wenn die aktuelle Transaktion
   tatsächlich keiner der vorhandenen Kategorien zuverlässig
   zugeordnet werden kann.

8. Die Begründung darf sich ausschließlich auf Informationen
   beziehen, die in der aktuellen Transaktion oder den angegebenen
   historischen Beispielen enthalten sind.

9. Gib ausschließlich gültiges JSON zurück.

10. Die Kategorie muss exakt einer der vorgegebenen Kategorien
    entsprechen.

AKTUELLE TRANSAKTION:

{transaction_text}

HISTORISCHE BEISPIELE:

{rag_context}

Antworte exakt in diesem Format:

{{
  "category": "Kategorie aus der Liste",
  "subcategory": "kurze Unterkategorie",
  "confidence": 0.0,
  "reason": "kurze Begründung ausschließlich anhand der vorhandenen Informationen"
}}
""".strip()


def categorize_transaction_with_rag(
    transaction: dict,
    collection,
) -> dict:
    """
    Kategorisiert eine Transaktion mit RAG + Qwen.
    """

    query = (
        transaction.get("merchant_normalized")
        or transaction.get("merchant")
        or ""
    )

    description = clean_transaction_text(
        transaction.get("description", "")
    )

    if description:
        query = f"{query} {description}"

    results = hybrid_search(
        collection,
        query,
        exact_limit=8,
        semantic_limit=8,
    )

    rag_context = build_rag_context(results)

    prompt = build_prompt(
        transaction,
        rag_context,
    )

    response = ollama.chat(
        model=LLM_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        format="json",
        options={
            "temperature": 0,
        },
    )

    content = response["message"]["content"]

    try:
        result = json.loads(content)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "LLM hat kein gültiges JSON zurückgegeben:\n"
            f"{content}"
        ) from exc

    category = result.get("category")

    if category not in CATEGORIES:
        raise RuntimeError(
            f"LLM hat ungültige Kategorie geliefert: "
            f"{category!r}"
        )

    confidence = result.get("confidence")

    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        confidence = None

    return {
        "category": category,
        "subcategory": result.get("subcategory"),
        "confidence": confidence,
        "reason": result.get("reason", ""),
        "rag_match_type": results.get(
            "match_type"
        ),
        "rag_matches": (
            results.get("exact")
            or results.get("semantic")
            or []
        ),
    }