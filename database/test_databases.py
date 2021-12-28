import time
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from account.account import Account
from database.database import ObjectNotFound, Database
from database.implementations.mysql_database import DatabaseMySQL
from transaction.transaction import Transaction
from transaction_manager.status import TransactionStatus


def get_transaction(source: Account, target: Account) -> Transaction:
    return Transaction(
        id_=uuid4(),
        source_account=source.id_,
        target_account=target.id_,
        currency=source.currency,
        balance_brutto=Decimal(10000),
        balance_netto=Decimal(9900),
        status=TransactionStatus.PENDING,
        timestamp=datetime.now().replace(microsecond=0),
    )


class TestAllDatabases:

    def test_connection(self, connection_dict: dict) -> None:
        database = DatabaseMySQL(connection=connection_dict)
        database.save_account(Account.random())
        all_accounts = database.get_accounts()
        print(all_accounts)
        database.close_connection()

    def test_all_dbs(self, database_connected: Database, connection_dict: dict) -> None:
        database_connected.clear_all_test(db_name=connection_dict["database"])
        account = Account.random()
        account2 = Account.random()
        database_connected.save_account(account)
        database_connected.save_account(account2)
        got_account = database_connected.get_account(account.id_)
        assert account == got_account

        not_account = database_connected.get_account(uuid4())
        assert not_account is None

        all_objects = database_connected.get_accounts()
        assert len(all_objects) == 2
        for acc in all_objects:
            assert isinstance(acc, Account)

        account.currency = "USD"
        database_connected.save_account(account)
        got_account = database_connected.get_account(account.id_)
        assert account == got_account

        # TODO: test transactions
        account3 = Account.random()
        account4 = Account.random()
        database_connected.save_account(account3)
        database_connected.save_account(account4)

        transaction = get_transaction(account3, account4)
        database_connected.save_transaction(transaction)

        assert transaction == database_connected.get_transaction(transaction.id_)
        assert [transaction] == database_connected.get_single_account_transactions(transaction.source_account)
        assert [transaction] == database_connected.get_single_account_transactions(transaction.target_account)

        # # test delete methods
        # # deleting existing data
        # database_connected.delete(account.id_)
        # with pytest.raises(ObjectNotFound):
        #     database_connected.get_object(account.id_)
        #
        # # trying to delete nonexistent data
        # all_accounts_1 = database_connected.get_objects()
        # database_connected.delete(account.id_)   # using previously deleted account id
        # all_accounts_2 = database_connected.get_objects()
        # assert all_accounts_1 == all_accounts_2
