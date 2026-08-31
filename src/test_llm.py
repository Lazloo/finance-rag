from llm_categorizer import classify_with_ollama
from models import Transaction


transaction = Transaction(
    bank="comdirect",
    booking_date="23.06.2026",
    value_date=None,
    transaction_type="Lastschrift",
    merchant=(
        "SumUp *Hutz GbR "
        "SumUp *Hutz GbR, Korschenbroic DE "
        "Karte Nr. 4871 78XX XXXX 9343 "
        "Kartenzahlung comdirect Visa-Debitkarte "
        "2026-06-21 00:00:00"
    ),
    amount=-12.20,
    description="",
)


result = classify_with_ollama(
    transaction
)


print(result)