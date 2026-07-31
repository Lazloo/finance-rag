from dataclasses import dataclass


@dataclass(slots=True)
class Transaction:
    bank: str
    booking_date: str
    value_date: str | None
    transaction_type: str
    merchant: str
    amount: float
    description: str
    reference: str | None = None