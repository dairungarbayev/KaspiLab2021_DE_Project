from datetime import datetime
from decimal import Decimal
from uuid import uuid4, UUID

import pytest

from account.account import Account, CurrencyMismatchError


class TestAccount:
    def test_account_create(self) -> None:
        creation_time = datetime.now()
        account = Account(
            id_=uuid4(),
            currency="KZT",
            balance=Decimal(10),
            creation_timestamp=creation_time,
        )
        assert isinstance(account, Account)
        assert account.balance == 10

        account2 = Account(
            id_=uuid4(),
            currency="KZT",
            balance=Decimal(5),
            creation_timestamp=creation_time,
        )

        assert account2 < account

    def test_errors(self) -> None:
        account = Account(
            id_=uuid4(),
            currency="KZT",
            balance=Decimal(10),
            creation_timestamp=datetime.now(),
        )

        account2 = Account(
            id_=uuid4(),
            currency="USD",
            balance=Decimal(5),
            creation_timestamp=datetime.now(),
        )

        with pytest.raises(CurrencyMismatchError):
            assert account2 < account

