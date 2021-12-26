from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from uuid import UUID


@dataclass
class Transaction:
    id_: Optional[UUID]
    source_account: UUID
    target_account: UUID
    balance_brutto: Decimal
    balance_netto: Optional[Decimal]
    currency: str
    status: str
    timestamp: int  # when transaction happens
