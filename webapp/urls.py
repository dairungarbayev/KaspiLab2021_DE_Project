"""webapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from webapp import views

urlpatterns = [
    path('', views.redirect_to_list),
    path('accounts/', views.accounts_list, name='accounts_list'),
    path('accounts/<uuid:account_id>', views.account_transactions, name='transactions_list'),
    path('accounts/<uuid:account_id>/transfer', views.transfer),
    path('accounts/create_account/', views.create_account),
]
