from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from account.account import Account
from database.database import Database
from transaction.transaction import Transaction
from transaction_manager.manager import TransactionManager
from transaction_manager.status import TransactionStatus


def get_account() -> Account:
    return Account(
        id_=uuid4(),
        currency='KZT',
        balance=Decimal(5000),
        creation_timestamp=datetime.now(),
    )


class TestTransactionManager:

    def test_deposit_transfer(self, database_connected: Database) -> None:
        account1 = get_account()
        account2 = get_account()
        database_connected.save_account(account1)
        database_connected.save_account(account2)

        manager = TransactionManager(database=database_connected)

        transaction = Transaction.get_transaction(account1, account2)

        manager.transfer(transaction)

        saved_transaction = database_connected.get_transaction(transaction.id_)
        assert saved_transaction.status == TransactionStatus.FULFILLED

        account1_new = database_connected.get_account(account1.id_)
        account2_new = database_connected.get_account(account2.id_)

        assert account1_new.balance == account1.balance - transaction.balance_brutto
        assert account2_new.balance == account2.balance + transaction.balance_netto

        # transaction with same account
        transaction2 = Transaction(
            id_=uuid4(),
            source_account=uuid4(),
            target_account=account1.id_,
            balance_brutto=Decimal(500),
            balance_netto=None,
            currency=account1_new.currency,
            status=TransactionStatus.PENDING,
            timestamp=datetime.now(),
        )
        result1 = manager.cash_deposit(transaction2)
        account1_deposited = database_connected.get_account(account1.id_)
        assert account1_deposited.balance == account1_new.balance + transaction2.balance_netto
        assert result1 == "Successful deposit"

        # trying to pass the transaction2 again
        transaction2.currency = "USD"
        result2 = manager.cash_deposit(transaction2)
        assert result2 == "Transaction already fulfilled"
