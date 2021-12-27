from django import forms


class CreateAccountForm(forms.Form):
    currency = forms.CharField(label='currency')

