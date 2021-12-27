from django import forms


class CreateAccountForm(forms.Form):
    currency = forms.CharField(label='currency')


class TransferCashForm(forms.Form):
    amount = forms.CharField()
    target_account = forms.CharField()


class DepositCashForm(forms.Form):
    deposit_amount = forms.CharField()

