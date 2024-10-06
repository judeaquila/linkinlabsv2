from django import forms

class CardPaymentForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Enter amount to deposit'
        )