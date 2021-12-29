from django import forms

CHOICES = (('KZT', 'KZT'), ('USD', 'USD'), ('EUR', 'EUR'))


class CreateAccountForm(forms.Form):
    currency = forms.ChoiceField(choices=CHOICES)


class TransferCashForm(forms.Form):
    amount = forms.FloatField()
    target_account = forms.UUIDField()


class DepositCashForm(forms.Form):
    deposit_amount = forms.FloatField()

