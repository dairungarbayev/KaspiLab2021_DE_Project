from uuid import UUID

from django.http import HttpRequest, HttpResponse

from django.shortcuts import render

from database.implementations.mysql_database import DatabaseMySQL

PASS = "10Guine@Pig$@teLion"     # TODO: read from environment variables

connection = {"host": "localhost",
              "user": "root",
              "password": PASS,
              "database": "dbtest"
              }

database = DatabaseMySQL(connection=connection)


def index(request: HttpRequest) -> HttpResponse:
    accounts = database.get_accounts()
    return render(request, "index.html", context={"accounts": accounts})


def account_transactions(request: HttpRequest, account_id: UUID) -> HttpResponse:
    acc_transactions = database.get_single_account_transactions(account_id=account_id)
    return render(request, "account_transactions.html", context={"account_transactions": acc_transactions})
