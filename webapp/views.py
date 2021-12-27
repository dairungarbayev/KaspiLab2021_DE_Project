from decimal import Decimal
from uuid import UUID, uuid4

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect

from django.shortcuts import render
from django.urls import reverse

from account.account import Account
from database.implementations.mysql_database import DatabaseMySQL
from webapp import forms

PASS = "10Guine@Pig$@teLion"     # TODO: read from environment variables

connection = {"host": "localhost",
              "user": "root",
              "password": PASS,
              "database": "dbtest"
              }

database = DatabaseMySQL(connection=connection)


def redirect_to_list(request: HttpRequest) -> HttpResponse:
    return HttpResponseRedirect('accounts/')


def accounts_list(request: HttpRequest) -> HttpResponse:
    accounts = database.get_accounts()
    return render(request, "index.html", context={"accounts": accounts})


def account_transactions(request: HttpRequest, account_id: UUID) -> HttpResponse:
    acc_transactions = database.get_single_account_transactions(account_id=account_id)
    return render(request, "account_transactions.html", context={"account_transactions": acc_transactions})


def create_account(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = forms.CreateAccountForm(request.POST)
        if form.is_valid():
            currency = form.cleaned_data['currency']
            database.save_account(Account(id_=uuid4(), currency=currency, balance=Decimal(0)))
            return HttpResponseRedirect(reverse('accounts_list'))
    return render(request, "add_account.html")

