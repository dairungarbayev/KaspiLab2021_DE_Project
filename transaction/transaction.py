from dataclasses import dataclass
from datetime import datetime
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
    timestamp: datetime  # when transaction happens

    # TODO: raise exception if source and target currencies and currency do not match
