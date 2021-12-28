from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from account.account import Account
from transaction_manager.status import TransactionStatus


@dataclass
class Transaction:
    id_: Optional[UUID]
    source_account: UUID
    target_account: UUID
    balance_brutto: Optional[Decimal]
    balance_netto: Optional[Decimal]
    currency: str
    status: str
    timestamp: datetime  # when transaction happens

    # factory method for tests
    @classmethod
    def get_transaction(cls, source: Account, target: Account) -> "Transaction":
        return cls(
            id_=uuid4(),
            source_account=source.id_,
            target_account=target.id_,
            currency=source.currency,
            balance_brutto=Decimal(1000),
            balance_netto=Decimal(990),
            status=TransactionStatus.PENDING,
            timestamp=datetime.now().replace(microsecond=0),
        )
