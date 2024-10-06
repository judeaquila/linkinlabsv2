from django.contrib import admin
from .models import GeneralCategory, Category, SampleDelivery, Test, PricingOption, TestPrice, TestRequest

# MODELS.
admin.site.register(GeneralCategory)
admin.site.register(Category)
admin.site.register(SampleDelivery)
admin.site.register(Test)
admin.site.register(PricingOption)
admin.site.register(TestPrice)
admin.site.register(TestRequest)