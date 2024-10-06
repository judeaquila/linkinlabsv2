from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, UserSocial

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'username']

class EditUserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'street_address', 'street_address_two', 'phone_number', 'city', 'company']

class EditUserSocialForm(forms.ModelForm):
    class Meta:
        model = UserSocial
        fields = ['facebook', 'instagram', 'twitter', 'tiktok']