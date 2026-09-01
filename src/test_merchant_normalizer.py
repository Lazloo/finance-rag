from models import Transaction
from merchant_normalizer import normalize_merchant


examples = [
    Transaction(
        bank="ING",
        booking_date="01.07.2026",
        value_date="01.07.2026",
        transaction_type="Lastschrift",
        merchant=(
            "Baeckerei Schneider Baeckerei Schneider, "
            "Duesseldorf DE"
        ),
        amount=-5.50,
        description="",
    ),

    Transaction(
        bank="ING",
        booking_date="01.07.2026",
        value_date="01.07.2026",
        transaction_type="Lastschrift",
        merchant="Nexi Germany GmbH",
        amount=-6.48,
        description=(
            "PAENZ AMP PIEPMATZ Vielen Dank "
            "Korschenbroich"
        ),
    ),

    Transaction(
        bank="comdirect",
        booking_date="23.06.2026",
        value_date="23.06.2026",
        transaction_type="Lastschrift",
        merchant=(
            "EDK*FRISCHEC RAEDLE "
            "EDK*FRISCHEC RAEDLE, KORSCHENBROIC "
            "DE Karte Nr. 4871 78XX XXXX 9343"
        ),
        amount=-49.59,
        description="",
    ),

    Transaction(
        bank="ING",
        booking_date="21.07.2026",
        value_date="21.07.2026",
        transaction_type="Lastschrift",
        merchant="HAGEBAU SAGT DANKE",
        amount=-25.00,
        description="",
    ),

    Transaction(
        bank="ING",
        booking_date="30.07.2026",
        value_date="30.07.2026",
        transaction_type="Lastschrift",
        merchant="JEANS FRITZ",
        amount=-29.90,
        description="",
    ),
]


for transaction in examples:

    normalize_merchant(transaction)

    print(
        f"{transaction.merchant}"
    )

    print(
        "  ->",
        transaction.merchant_normalized
    )

    print()