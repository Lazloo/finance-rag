from dataclasses import dataclass


@dataclass
class Transaction:

    booking_date: str

    value_date: str | None

    transaction_type: str

    merchant: str

    amount: float

    description: str

    bank: str