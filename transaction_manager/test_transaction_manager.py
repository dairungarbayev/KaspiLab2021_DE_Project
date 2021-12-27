from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from account.account import Account
from database.database import Database
from transaction.transaction import Transaction
from transaction_manager.manager import TransactionManager


def get_transaction(source: Account, target: Account) -> Transaction:
    now = datetime.now()
    now = datetime(year=now.year,
                   month=now.month,
                   day=now.day,
                   hour=now.hour,
                   minute=now.minute,
                   second=now.second)
    return Transaction(
        id_=uuid4(),
        source_account=source.id_,
        target_account=target.id_,
        currency=source.currency,
        balance_brutto=Decimal(1000),
        balance_netto=Decimal(990),
        status='pending',   # TODO: ---------------------------------------------------
        timestamp=now,
    )


def get_account() -> Account:
    return Account(
        id_=uuid4(),
        currency='KZT',
        balance=Decimal(5000),
    )


class TestTransactionManager:

    def test_deposit_transfer(self, database_connected: Database) -> None:
        account1 = get_account()
        account2 = get_account()
        database_connected.save_account(account1)
        database_connected.save_account(account2)

        manager = TransactionManager(database=database_connected)

        transaction = get_transaction(account1, account2)

        manager.transfer(transaction)

        saved_transaction = database_connected.get_transaction(transaction.id_)
        assert saved_transaction.status == 'fulfilled'

        account1_new = database_connected.get_account(account1.id_)
        account2_new = database_connected.get_account(account2.id_)

        assert account1_new.balance == account1.balance - transaction.balance_brutto
        assert account2_new.balance == account2.balance + transaction.balance_netto

        # transaction with same account

