from typing import List, Optional
from uuid import UUID, uuid4

import mysql.connector
import pandas as pd
from pandas import Series

from database.database import Database, ObjectNotFound
from transaction.transaction import Transaction


class TransactionDatabaseMySQL(Database):

    def __init__(self, connection: dict):
        self.conn = mysql.connector.connect(
            host=connection['host'],
            user=connection['user'],
            passwd=connection['password'],
            database=connection['database']
        )
        cursor = self.conn.cursor()
        cursor.execute("""
                    CREATE TABLE IF NOT EXISTS transactions (
                        id VARCHAR PRIMARY KEY,
                        source_account VARCHAR,
                        target_account VARCHAR,
                        currency VARCHAR,
                        balance_brutto DECIMAL,
                        balance_netto DECIMAL,
                        status VARCHAR,
                        timestamp NUMBER
                    );
                """)
        self.conn.commit()

    def close_connection(self):
        self.conn.close()

    def save(self, transaction: Transaction) -> None:
        if transaction.id_ is None:
            transaction.id_ = uuid4()

        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id FROM transactions
            WHERE id = %s;
        """, (str(transaction.id_),))
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

    def update(self, transaction: Transaction) -> None:
        pass

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

    def clear_all(self) -> None:
        pass

    def get_objects(self) -> Optional[List[Transaction]]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM accounts;")
        data = cur.fetchall()
        if len(data) == 0:
            return None
        cols = [x[0] for x in cur.description]
        df = pd.DataFrame(data, columns=cols)
        return [self.pandas_row_to_transaction(row) for index, row in df.iterrows()]

    def get_object(self, id_: UUID) -> Optional[Transaction]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM accounts WHERE id = %s;", (str(id_),))

        data = cur.fetchall()
        if len(data) == 0:
            return None
        cols = [x[0] for x in cur.description]
        df = pd.DataFrame(data, columns=cols)
        return self.pandas_row_to_transaction(row=df.iloc[0])
