from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


PAYMENT_CHOICES = (
    # ('S', 'Stripe'),
    # ('P', 'PayPal'),
    ('M', 'Momo'),
)


class CheckoutForm(forms.Form):
    examination_date = forms.DateTimeField(input_formats=['%m/%d/%Y %I:%M %p'], required=True)
    address = forms.CharField(required=True)
    description = forms.CharField(required=True)
    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)
