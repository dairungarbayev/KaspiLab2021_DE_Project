import random
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4


class CurrencyMismatchError(ValueError):
    pass


@dataclass
class Account:
    id_: Optional[UUID]
    currency: str
    balance: Decimal
    creation_timestamp: datetime

    def __lt__(self, other: "Account") -> bool:
        assert isinstance(other, Account)
        if self.currency != other.currency:
            raise CurrencyMismatchError
        return self.balance < other.balance

    @classmethod
    def random(cls) -> "Account":  # Factory
        return cls(
            id_=uuid4(),
            currency="KZT",
            balance=Decimal(random.randint(1, 1000)),
            creation_timestamp=datetime.now().replace(microsecond=0),
        )
