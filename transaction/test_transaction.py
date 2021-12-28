from datetime import datetime
from time import sleep
from decimal import Decimal
from uuid import uuid4, UUID

from account.account import Account
from transaction.transaction import Transaction
from transaction_manager.status import TransactionStatus


class TestTransactions:

    def test_create_transaction(self) -> None:
        account1 = Account.random()
        account2 = Account.random()
        transaction = Transaction(
            id_=uuid4(),
            source_account=account1.id_,
            target_account=account2.id_,
            timestamp=datetime.now().replace(microsecond=0),
            currency='USD',
            balance_brutto=Decimal(500),
            balance_netto=Decimal(480),
            status=TransactionStatus.FULFILLED,
        )

        assert isinstance(transaction, Transaction)
        assert isinstance(transaction.source_account, UUID)
        assert isinstance(transaction.target_account, UUID)
        assert transaction.status == TransactionStatus.FULFILLED

    def test_less_greater_than(self) -> None:
        account1 = Account.random()
        account2 = Account.random()
        transaction1 = Transaction.get_transaction(account1, account2)
        sleep(1)
        transaction2 = Transaction.get_transaction(account1, account2)
        assert transaction1 < transaction2
        assert transaction2 > transaction1
