from django import forms
from .models import TestRequest, Test, SampleDelivery, Category, PricingOption

class TestRequestForm(forms.ModelForm):
    test = forms.ModelChoiceField(
        queryset=Test.objects.all(),
        empty_label='Choose a Test',
        help_text='Select from standard or customized laboratory tests.'
    )
    
    delivery_method = forms.ModelChoiceField(
        queryset=SampleDelivery.objects.all(),
        empty_label='Choose a Delivery Option',
        help_text='Courier pickup is available upon request.'
    )

    test_category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label='Choose a Product Category',
        help_text='Please specify if the food sample is locally produced or imported.'
    )

    price_option = forms.ModelChoiceField(
        queryset=PricingOption.objects.all(),
        empty_label='Choose a Pricing Option',
        help_text='Regular: 4–8 weeks | Deluxe: 3–4 weeks | Premium: 8–12 days | Express: 3–8 days'
    )

    test_price = forms.DecimalField(
        widget=forms.HiddenInput(),
        required=False,
    )

    class Meta:
        model = TestRequest
        fields = ['test', 'test_category', 'price_option', 'delivery_method']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Base styling class string for all text and select dropdown fields
        field_classes = (
            'mt-1.5 block w-full rounded-xl border border-slate-200 bg-white '
            'px-3.5 py-2.5 text-sm text-slate-900 shadow-sm transition-colors '
            'placeholder:text-slate-400 focus:border-slate-900 focus:outline-none '
            'focus:ring-1 focus:ring-slate-900'
        )
        
        # Apply Tailwind configuration to fields loop dynamically
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.HiddenInput):
                # Update widget element layout classes
                field.widget.attrs.update({'class': field_classes})
                
                # Format default help text parameters nicely beneath inputs
                if field.help_text:
                    field.help_text = f'<p class="mt-2 text-xs leading-relaxed text-slate-400">{field.help_text}</p>'


# ADMIN UPDATE TEST STATUS
class TestStatusForm(forms.ModelForm):
    class Meta:
        model = TestRequest
        fields = ['delivery_status']