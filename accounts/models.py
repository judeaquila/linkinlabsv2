from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

# USER PROFILE.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, verbose_name=_('First Name'), blank=False, null=False)
    last_name = models.CharField(max_length=50, verbose_name=_('Last Name'), blank=True, null=True)
    street_address = models.CharField(max_length=100, verbose_name=_('Street Address 1'), blank=False, null=False)
    street_address_two = models.CharField(max_length=100, verbose_name=_('Street Address 2'), blank=True, null=True)
    phone_number = models.CharField(max_length=15, verbose_name=_('Phone Number'), blank=False, null=False)
    city = models.CharField(max_length=50, blank=False, null=False)
    company = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    
class UserSocial(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    facebook = models.CharField(max_length=50, blank=True, null=True)
    instagram = models.CharField(max_length=50, blank=True, null=True)
    twitter = models.CharField(max_length=50, blank=True, null=True)
    tiktok = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s social account"