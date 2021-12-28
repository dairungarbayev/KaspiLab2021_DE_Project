from decimal import Decimal
from uuid import uuid4

from database.database import Database
from transaction.transaction import Transaction
from transaction_manager.status import TransactionStatus


class TransactionManager:

    def __init__(self, database: Database):
        self.database = database
        self.commission_percentage = 0.0

    def set_balance_netto(self, transaction: Transaction) -> None:
        # just use a single commission policy for all transactions
        # a more complex policy can be implemented later
        if transaction.balance_netto is None:
            ratio = Decimal(1) - Decimal(self.commission_percentage) / Decimal(100)
            transaction.balance_netto = transaction.balance_brutto * ratio

    def set_balance_brutto(self, transaction: Transaction) -> None:
        if transaction.balance_brutto is None:
            ratio = Decimal(1) - Decimal(self.commission_percentage) / Decimal(100)
            transaction.balance_brutto = transaction.balance_netto / ratio

    def cash_deposit(self, transaction: Transaction) -> str:
        if transaction.id_ is None:
            transaction.id_ = uuid4()
        self.set_balance_netto(transaction)
        account = self.database.get_account(transaction.target_account)

        if transaction.status == 'fulfilled':
            return "Transaction already fulfilled"
        if transaction.currency != account.currency:
            return "Currencies do not match"

        account.balance += transaction.balance_netto
        self.database.save_account(account)
        transaction.status = TransactionStatus.FULFILLED
        self.database.save_transaction(transaction)
        return "Successful deposit"

    def transfer(self, transaction: Transaction) -> str:
        if transaction.id_ is None:
            transaction.id_ = uuid4()

        self.set_balance_brutto(transaction)

        if transaction.source_account == transaction.target_account:
            return "Transaction denied. Both accounts are the same."

        if transaction.status == TransactionStatus.FULFILLED:
            return "Transaction already fulfilled"
        target_account = self.database.get_account(transaction.target_account)
        if transaction.currency != target_account.currency:
            return "Currencies do not match"
        source_account = self.database.get_account(transaction.source_account)
        if source_account.balance < transaction.balance_brutto:
            return "Insufficient funds"

        target_account.balance += transaction.balance_netto
        source_account.balance -= transaction.balance_brutto
        self.database.save_account(source_account)
        self.database.save_account(target_account)
        transaction.status = TransactionStatus.FULFILLED
        self.database.save_transaction(transaction)
        return "Successful transaction"

    # TODO: transaction and account balances: enforce positive values!!!
    # TODO: commission for transfer and deposit separate, as read-only properties
