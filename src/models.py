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

    normalized_type: str = "unknown"
    is_internal_transfer: bool = False
    category: str | None = None
    subcategory: str | None = None