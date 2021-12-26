from typing import List, Optional
from uuid import UUID, uuid4

import mysql.connector
import pandas as pd
from pandas import Series

from account.account import Account
from database.database import Database, ObjectNotFound


class AccountDatabaseMySQL(Database):

    def __init__(self, connection: dict):
        self.conn = mysql.connector.connect(
            host=connection['host'],
            user=connection['user'],
            passwd=connection['password'],
            database=connection['database']
        )
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id VARCHAR PRIMARY KEY,
                currency VARCHAR,
                balance DECIMAL
            );
        """)
        self.conn.commit()
        cursor.close()

    def close_connection(self):
        self.conn.close()

    def save(self, account: Account) -> None:
        if account.id_ is None:
            account.id_ = uuid4()

        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id FROM accounts
            WHERE id = %s;
        """, (str(account.id_),))
        if cursor.rowcount == 0:
            cursor.execute("""
                INSERT INTO accounts (id, currency, balance)
                VALUES (%s, %s, %s);
            """, (str(account.id_), account.currency, account.balance))
            self.conn.commit()
        cursor.close()

    def update(self, account: Account) -> None:
        pass

    def clear_all(self) -> None:
        pass

    def pandas_row_to_account(self, row: Series) -> Account:
        return Account(
            id_=UUID(row["id"]),
            currency=row["currency"],
            balance=row["balance"],
        )

    def get_objects(self) -> Optional[List[Account]]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM accounts;")
        data = cur.fetchall()
        if len(data) == 0:
            return None
        cols = [x[0] for x in cur.description]
        df = pd.DataFrame(data, columns=cols)
        return [self.pandas_row_to_account(row) for index, row in df.iterrows()]

    def get_object(self, id_: UUID) -> Optional[Account]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM accounts WHERE id = %s;", (str(id_),))

        data = cur.fetchall()
        if len(data) == 0:
            return None
        cols = [x[0] for x in cur.description]
        df = pd.DataFrame(data, columns=cols)
        return self.pandas_row_to_account(row=df.iloc[0])
