from django import forms
from .models import TestRequest, Test, SampleDelivery, Category, PricingOption

# Test Request Form for FDA/GSA Tests
class TestRequestForm(forms.ModelForm):
    test = forms.ModelChoiceField(
        queryset = Test.objects.all(),
        empty_label = 'Choose a Test',
        help_text = 'Choose among FDA/GSA Standard Tests and Customized Tests'
    )
    
    delivery_method = forms.ModelChoiceField(
        queryset = SampleDelivery.objects.all(),
        empty_label = 'Choose a Delivery Option',
        help_text = '*Courier Services are available on request.'
    )

    test_category = forms.ModelChoiceField(
        queryset = Category.objects.all(),
        empty_label = 'Choose a Product Category',
        help_text = 'Is your product locally-manufactured or imported?'
    )

    price_option = forms.ModelChoiceField(
        queryset = PricingOption.objects.all(),
        empty_label = 'Choose a Pricing Option',
        help_text = '*Regular: 4-8 weeks, Deluxe: 3-4 weeks, Premium: 8-12 days, Express: 3-8 days'
    )

    test_price = forms.DecimalField(
        widget = forms.HiddenInput(),
        required = False,
    )

    # class Meta:
    #     model = TestRequest
    #     fields = ['test', 'test_category', 'delivery_method']

    class Meta:
        model = TestRequest
        fields = ['test', 'test_category', 'price_option', 'delivery_method']


# ADMIN UPDATE TEST STATUS
class TestStatusForm(forms.ModelForm):
    class Meta:
        model = TestRequest
        fields = ['delivery_status']