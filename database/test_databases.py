
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from account.account import Account
from database.database import ObjectNotFound, Database
from database.implementations.mysql_database import DatabaseMySQL
from transaction.transaction import Transaction
from transaction_manager.status import TransactionStatus


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

        transaction = Transaction.get_transaction(account3, account4)
        database_connected.save_transaction(transaction)

        assert transaction == database_connected.get_transaction(transaction.id_)
        assert [transaction] == database_connected.get_single_account_transactions(transaction.source_account)
        assert [transaction] == database_connected.get_single_account_transactions(transaction.target_account)

