from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from account.account import Account
from transaction.transaction import Transaction


class ObjectNotFound(ValueError):
    ...


@dataclass
class Database(ABC):

    # Accounts

    @abstractmethod
    def save_account(self, account: Account) -> None:
        pass

    @abstractmethod
    def clear_all_test(self, db_name: str) -> None:
        pass

    @abstractmethod
    def get_accounts(self) -> Optional[List[Account]]:
        pass

    @abstractmethod
    def get_account(self, id_: UUID) -> Optional[Account]:
        pass

    # Transactions

    @abstractmethod
    def save_transaction(self, transaction: Transaction) -> None:
        pass

    @abstractmethod
    def get_all_transactions(self) -> Optional[List[Transaction]]:
        pass

    @abstractmethod
    def get_single_account_transactions(self, account_id: UUID) -> Optional[List[Transaction]]:
        pass

    @abstractmethod
    def get_transaction(self, id_: UUID) -> Optional[Transaction]:
        pass
