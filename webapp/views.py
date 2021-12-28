import os
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect

from django.shortcuts import render
from django.urls import reverse

from account.account import Account
from database.implementations.mysql_database import DatabaseMySQL
from transaction.transaction import Transaction
from transaction_manager.manager import TransactionManager
from webapp import forms

PASS = "10Guine@Pig$@teLion"     # TODO: read from environment variables
# PASS = os.getenv("MySQL_local_password")   # TODO: restart machine

connection = {"host": "localhost",
              "user": "root",
              "password": PASS,
              "database": "dbtest"
              }

database = DatabaseMySQL(connection=connection)
transaction_manager = TransactionManager(database=database)

# client_id = UUID("5309c77a-9487-49d6-9185-6dae9f9c79ed")
client_id = UUID("aaaaaaaa-0000-aaaa-0000-aaaaaaaaaaaa")

def redirect_to_list(request: HttpRequest) -> HttpResponse:
    return HttpResponseRedirect('accounts/')


def accounts_list(request: HttpRequest) -> HttpResponse:
    accounts = database.get_accounts()
    return render(request, "index.html", context={"accounts": accounts})


def account_transactions(request: HttpRequest, account_id: UUID) -> HttpResponse:
    account = database.get_account(account_id)
    acc_transactions = database.get_single_account_transactions(account_id=account_id)
    return render(request,
                  "account_transactions.html",
                  context={"account_transactions": acc_transactions,
                           "account": account})


def create_account(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = forms.CreateAccountForm(request.POST)
        if form.is_valid():
            currency = form.cleaned_data['currency']
            database.save_account(Account(id_=uuid4(), currency=currency, balance=Decimal(0)))
            return HttpResponseRedirect(reverse('accounts_list'))
    return render(request, "add_account.html")


def transfer(request: HttpRequest, account_id: UUID) -> HttpResponse:
    source_account = database.get_account(account_id)

    if request.method == 'POST':
        form = forms.TransferCashForm(request.POST)
        if form.is_valid():
            balance_brutto = form.cleaned_data['amount']
            target_account = form.cleaned_data['target_account']
            transaction = Transaction(
                id_=uuid4(),
                source_account=source_account.id_,
                target_account=UUID(target_account),
                balance_brutto=Decimal(balance_brutto),
                balance_netto=None,
                currency=source_account.currency,
                status='pending',
                timestamp=datetime.now(),
            )
            result = transaction_manager.transfer(transaction)
            # if result == "Successful transaction":
            #     return HttpResponseRedirect(reverse('transactions_list'))
    return render(request, "transfer.html", context={"source_account": source_account})


def deposit_cash(request: HttpRequest, account_id: UUID) -> HttpResponse:
    account = database.get_account(account_id)
    if request.method == 'POST':
        form = forms.DepositCashForm(request.POST)
        if form.is_valid():
            balance_brutto = form.cleaned_data['deposit_amount']
            transaction = Transaction(
                id_=uuid4(),
                source_account=client_id,
                target_account=account_id,
                balance_brutto=Decimal(balance_brutto),
                balance_netto=None,
                currency=account.currency,
                status='pending',
                timestamp=datetime.now(),
            )
            result = transaction_manager.cash_deposit(transaction)
    return render(request, "cash_deposit.html", context={"account": account})

# TODO: deposit, transfer and create_account center, add titles and labels and instructions, show result, make pretty
# TODO: maybe make source_id in transaction optional for depositing, enforce source_id in TransactionManager
