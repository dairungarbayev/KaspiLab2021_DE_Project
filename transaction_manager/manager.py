from decimal import Decimal
from uuid import uuid4

from database.database import Database
from transaction.transaction import Transaction


class TransactionManager:

    def __init__(self, database: Database):
        self.database = database
        self.commission_percentage = 0.0

    def set_balance_netto(self, transaction: Transaction) -> None:
        # just use a single commission policy for all transactions
        # a more complex policy can be implemented later
        transaction.balance_netto = transaction.balance_brutto * Decimal(1-self.commission_percentage/100)

    def cash_deposit(self, transaction: Transaction) -> None:
        if transaction.id_ is None:
            transaction.id_ = uuid4()
        self.set_balance_netto(transaction)
        account = self.database.get_account(transaction.target_account)
        if transaction.status != 'fulfilled':  # TODO: read statuses from a special class ------------------------------
            if transaction.currency == account.currency:
                account.balance += transaction.balance_netto
                self.database.save_account(account)
                transaction.status = 'fulfilled'  # TODO: --------------------------------------------------------------
                self.database.save_transaction(transaction)
            else:
                print("Currencies do not match")

    def transfer(self, transaction: Transaction) -> None:
        if transaction.id_ is None:
            transaction.id_ = uuid4()
        self.set_balance_netto(transaction)
        if transaction.source_account == transaction.target_account:
            print("Transaction denied. Both accounts are the same.")
            return None
        target_account = self.database.get_account(transaction.target_account)
        if transaction.status != 'fulfilled':  # TODO: -----------------------------------------------------------------
            if transaction.currency == target_account.currency:
                source_account = self.database.get_account(transaction.source_account)
                target_account += transaction.balance_netto
                source_account -= transaction.balance_brutto
                self.database.save_account(source_account)
                self.database.save_account(target_account)
                transaction.status = 'fulfilled'  # TODO: --------------------------------------------------------------
                self.database.save_transaction(transaction)
            else:
                print("Currencies do not match")

    # TODO: handle transaction balance_netto, set it Optional
    # TODO: transaction and account balances: enforce positive values!!!
    # TODO: error handling, send message back
