import os
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

import plotly
import plotly.graph_objs as go
import plotly.express as px

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect

from django.shortcuts import render
from django.urls import reverse

from account.account import Account
from database.implementations.mysql_database import DatabaseMySQL
from transaction.transaction import Transaction
from transaction_manager.manager import TransactionManager
from transaction_manager.status import TransactionStatus
from webapp import forms


connection = {"host": "localhost",
              "user": "root",
              "password": os.getenv("MYSQL_LOCAL_PASSWORD"),
              "database": "kldb"
              }

database = DatabaseMySQL(connection=connection)
transaction_manager = TransactionManager(database=database)

# client_id = UUID("5309c77a-9487-49d6-9185-6dae9f9c79ed")
client_id = UUID("aaaaaaaa-0000-aaaa-0000-aaaaaaaaaaaa")


def redirect_to_list(request: HttpRequest) -> HttpResponse:
    return HttpResponseRedirect('accounts/')


def accounts_list(request: HttpRequest) -> HttpResponse:
    accounts = database.get_accounts()
    maxvals = {}
    maxval_ids = []
    if accounts is not None:
        for acc in accounts:
            if acc.currency not in maxvals.keys() or acc.balance > maxvals[acc.currency]:
                maxvals[acc.currency] = acc.balance
        for acc in accounts:
            if acc.balance == maxvals[acc.currency]:
                maxval_ids.append(acc.id_)
    return render(request, "index.html", context={"accounts": accounts, "maxval_ids": maxval_ids})


def account_transactions(request: HttpRequest, account_id: UUID) -> HttpResponse:
    account = database.get_account(account_id)
    acc_transactions = database.get_single_account_transactions(account_id=account_id)

    graph_div = ''
    # create balance vs time plot
    if acc_transactions is not None:
        temp_balance = Decimal(0)
        time_x = [account.creation_timestamp.time()]
        balance_y = [Decimal(0)]
        for tr in acc_transactions:
            time_x.append(tr.timestamp.time())
            if account.id_ == tr.target_account:
                temp_balance = temp_balance + tr.balance_netto
            else:
                temp_balance = temp_balance - tr.balance_brutto
            balance_y.append(temp_balance)

        time_x.append(datetime.now().time())
        balance_y.append(account.balance)
        layout = go.Layout(
            title="Account Balance vs Time",
            xaxis=dict(
                title=""
            ),
            yaxis=dict(
                title=f"Balance {account.currency}"
            ))
        fig = go.Figure(layout=layout)
        fig.add_trace(go.Scatter(x=time_x, y=balance_y, line_shape="hv"))
        graph_div = plotly.offline.plot(fig, auto_open=False, output_type="div")

    return render(request,
                  "account_transactions.html",
                  context={"account_transactions": acc_transactions,
                           "account": account,
                           "graph_div": graph_div})


def create_account(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = forms.CreateAccountForm(request.POST)
        if form.is_valid():
            currency = form.cleaned_data['currency']
            database.save_account(Account(id_=uuid4(),
                                          currency=currency,
                                          balance=Decimal(0),
                                          creation_timestamp=datetime.now(),
                                          ))
            return HttpResponseRedirect(reverse('accounts_list'))
    return render(request, "add_account.html")


def transfer(request: HttpRequest, account_id: UUID) -> HttpResponse:
    source_account = database.get_account(account_id)
    result = ""
    if request.method == 'POST':
        form = forms.TransferCashForm(request.POST)
        if form.is_valid():
            balance_netto = form.cleaned_data['amount']
            target_account = form.cleaned_data['target_account']
            transaction = Transaction(
                id_=uuid4(),
                source_account=source_account.id_,
                target_account=UUID(target_account),
                balance_brutto=None,
                balance_netto=Decimal(balance_netto),
                currency=source_account.currency,
                status=TransactionStatus.PENDING,
                timestamp=datetime.now(),
            )
            result = transaction_manager.transfer(transaction)
            if result == "Successful transaction":
                source_account = database.get_account(account_id)  # reload account
    return render(request, "transfer.html", context={"source_account": source_account, "result": result})


def deposit_cash(request: HttpRequest, account_id: UUID) -> HttpResponse:
    account = database.get_account(account_id)
    result = ""
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
                status=TransactionStatus.PENDING,
                timestamp=datetime.now(),
            )
            result = transaction_manager.cash_deposit(transaction)
    return render(request, "cash_deposit.html", context={"account": account, "result": result})


