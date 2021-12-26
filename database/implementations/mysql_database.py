from typing import List, Optional
from uuid import UUID, uuid4

import mysql.connector
import pandas as pd
from pandas import Series

from account.account import Account
from database.database import Database, ObjectNotFound
from transaction.transaction import Transaction


class DatabaseMySQL(Database):

    def __init__(self, connection: dict):
        self.conn = mysql.connector.connect(
            host=connection["host"],
            user=connection["user"],
            password=connection["password"],
            database=connection["database"]
        )
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id VARCHAR(40) PRIMARY KEY,
                currency VARCHAR(5),
                balance DECIMAL);
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id VARCHAR(40) PRIMARY KEY,
                source_account VARCHAR(40),
                target_account VARCHAR(40),
                currency VARCHAR(5),
                balance_brutto DECIMAL,
                balance_netto DECIMAL,
                status VARCHAR(20),
                timestamp INT);
        """)
        self.conn.commit()
        cursor.close()

    def close_connection(self):
        self.conn.close()

    # Account methods

    def save_account(self, account: Account) -> None:
        if account.id_ is None:
            account.id_ = uuid4()

        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE accounts SET currency = %s, balance = %s WHERE id = %s;
        """, (account.currency, account.balance, str(account.id_)))

        if cursor.rowcount == 0:
            cursor.execute("""
                INSERT INTO accounts (id, currency, balance)
                VALUES (%s, %s, %s);
            """, (str(account.id_), account.currency, account.balance))
        self.conn.commit()
        cursor.close()

    def clear_all_test(self, db_name: str) -> None:
        if db_name == "dbtest":
            cur = self.conn.cursor()
            cur.execute("DELETE FROM accounts;")
            cur.execute("DELETE FROM transactions;")
            self.conn.commit()

    def pandas_row_to_account(self, row: Series) -> Account:
        return Account(
            id_=UUID(row["id"]),
            currency=row["currency"],
            balance=row["balance"],
        )

    def get_accounts(self) -> Optional[List[Account]]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM accounts;")
        data = cur.fetchall()
        if len(data) == 0:
            return None
        cols = [x[0] for x in cur.description]
        df = pd.DataFrame(data, columns=cols)
        return [self.pandas_row_to_account(row) for index, row in df.iterrows()]

    def get_account(self, id_: UUID) -> Optional[Account]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM accounts WHERE id = %s;", (str(id_),))

        data = cur.fetchall()
        if len(data) == 0:
            return None
        cols = [x[0] for x in cur.description]
        df = pd.DataFrame(data, columns=cols)
        return self.pandas_row_to_account(row=df.iloc[0])

    # Transaction methods

    def save_transaction(self, transaction: Transaction) -> None:
        if transaction.id_ is None:
            transaction.id_ = uuid4()

        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE transactions 
            SET 
                status = %s, 
            WHERE id = %s;
        """, (transaction.status, transaction.id_))
        if cursor.rowcount == 0:
            cursor.execute("""
                INSERT INTO accounts
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """, (str(transaction.id_),
                  str(transaction.source_account),
                  str(transaction.target_account),
                  transaction.currency,
                  transaction.balance_brutto,
                  transaction.balance_netto,
                  transaction.status,
                  transaction.timestamp,))
        self.conn.commit()
        cursor.close()

    def pandas_row_to_transaction(self, row: Series) -> Transaction:
        return Transaction(
            id_=UUID(row["id"]),
            source_account=UUID(row["source_account"]),
            target_account=UUID(row["target_account"]),
            currency=row["currency"],
            balance_brutto=row["balance_brutto"],
            balance_netto=row["balance_netto"],
            status=row["status"],
            timestamp=row["timestamp"],
        )

    def get_all_transactions(self) -> Optional[List[Transaction]]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM transactions;")
        data = cur.fetchall()
        if len(data) == 0:
            return None
        cols = [x[0] for x in cur.description]
        df = pd.DataFrame(data, columns=cols)
        return [self.pandas_row_to_transaction(row) for index, row in df.iterrows()]

    def get_single_account_transactions(self, account_id: UUID) -> Optional[List[Transaction]]:
        cur = self.conn.cursor()
        cur.execute("""
            SELECT * FROM transactions
            WHERE (source_account = %s) OR (target_account = %s);
        """, (str(account_id), str(account_id)))
        data = cur.fetchall()
        if len(data) == 0:
            return None
        cols = [x[0] for x in cur.description]
        df = pd.DataFrame(data, columns=cols)
        return [self.pandas_row_to_transaction(row) for index, row in df.iterrows()]

    def get_transaction(self, id_: UUID) -> Optional[Transaction]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM transactions WHERE id = %s;", (str(id_),))

        data = cur.fetchall()
        if len(data) == 0:
            return None
        cols = [x[0] for x in cur.description]
        df = pd.DataFrame(data, columns=cols)
        return self.pandas_row_to_transaction(row=df.iloc[0])

    # TODO: DataFrame from cursor.fetchall() method
    # TODO: TEST method that gets transactions associated with a specific account
