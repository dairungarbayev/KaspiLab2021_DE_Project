from django import forms


class CreateAccountForm(forms.Form):
    currency = forms.CharField(label='currency')


class TransferCashForm(forms.Form):
    amount = forms.CharField()
    target_account = forms.CharField()
