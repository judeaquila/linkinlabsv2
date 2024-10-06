from django.utils import timezone
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

# GENERAL TEST CATEGORY
class GeneralCategory(models.Model):
    CATEGORY_CHOICES = [
        ('FDA/GSA Standard Test', 'FDA/GSA Standard Test'),
        ('Custom Test', 'Custom Test'),
    ]
    name = models.CharField(max_length=100, choices=CATEGORY_CHOICES)

    class Meta:
        verbose_name_plural = 'General Categories'

    def __str__(self):
        return self.name

# FDA/GSA TEST CATEGORY
class Category(models.Model):
    CATEGORY_CHOICES = [
        ('Imported Product', 'Imported Product'),
        ('Locally Manufactured Product', 'Locally Manufactured Product'),
    ]

    name = models.CharField(max_length=100, choices=CATEGORY_CHOICES)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name
    
# DELIVERY METHOD
class SampleDelivery(models.Model):
    DELIVERY_OPTIONS = [
        ('Personal Delivery', 'Personal Delivery'),
        ('Courier Service', 'Courier Service'),
    ]

    delivery_method = models.CharField(max_length=50, choices=DELIVERY_OPTIONS)

    class Meta:
        verbose_name_plural = 'Sample Delivery Methods'

    def __str__(self):
        return self.delivery_method

# TEST    
class Test(models.Model):
    category = models.ForeignKey(GeneralCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    price_range = models.CharField(max_length=50, default='Unavailable')
    details = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

# PRICING OPTIONS
class PricingOption(models.Model):
    PRICING_OPTIONS = [
        ('Regular', 'Regular'),
        ('Deluxe', 'Deluxe'),
        ('Premium', 'Premium'),
        ('Express', 'Express'),
    ]

    name = models.CharField(max_length=10, choices=PRICING_OPTIONS)

    class Meta:
        verbose_name_plural = 'Pricing Options'

    def __str__(self):
        return self.name
    
# TEST PRICE
class TestPrice(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    pricing_option = models.ForeignKey(PricingOption, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('test', 'category', 'pricing_option')
        verbose_name_plural = 'Test Prices'

    def __str__(self):
        return f'{self.test} - {self.price}'

# TEST REQUEST 
class TestRequest(models.Model):
    TEST_DELIVERY_STATUS = [
        ('Pending', 'Pending'),
        ('Submitted', 'Submitted'),
        ('Confirmed', 'Confirmed'),
        ('Dispatched to Lab', 'Dispatched to Lab'),
        ('Completed', 'Completed'),
    ]

    TEST_PAYMENT_STATUS = [
        ('Paid', 'Paid'),
        ('Unpaid', 'Unpaid'),
    ]

    custom_id = models.CharField(max_length=12, blank=True, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    test_category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=_('Test Category'))
    delivery_method = models.ForeignKey(SampleDelivery, on_delete=models.CASCADE, verbose_name=_('Delivery Method'))
    price_option = models.ForeignKey(PricingOption, on_delete=models.CASCADE)
    test_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    delivery_status = models.CharField(max_length=100, choices=TEST_DELIVERY_STATUS, default='Pending')
    payment_status = models.CharField(max_length=10, choices=TEST_PAYMENT_STATUS, default='Unpaid')

    # Calculate Price
    def save(self, *args, **kwargs):
        price = TestPrice.objects.get(test=self.test, category=self.test_category, pricing_option=self.price_option)
        self.test_price = price.price
        super().save(*args, **kwargs)

    # Update Payment Status
    def update_payment_status(self, paid):
        if paid:
            self.payment_status = 'Paid'
        else:
            self.payment_status = 'Unpaid'
        self.save()

    # Generate Custom Test Request ID for Tracking
    def save(self, *args, **kwargs):
        if not self.custom_id:
            # Generate a custom ID
            self.custom_id = self.generate_custom_id()
        super(TestRequest, self).save(*args, **kwargs)

    # Generate ID
    def generate_custom_id(self):
        prefix = 'LKLABS'
        date_str = timezone.now().strftime('%Y%m%d')
        unique_part = uuid.uuid4().hex[:4].upper()
        return f'{prefix}-{date_str}-{unique_part}'

    class Meta:
        verbose_name_plural = 'Test Requests'

    def __str__(self):
        return f'{self.id} - {self.test} - {self.user.username}'
    
# USER ACTIVITY
class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=100)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.activity_type} - {self.timestamp}"