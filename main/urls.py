from django.urls import path
from .views import home, privacy, terms

urlpatterns = [
    path('', home, name='home'),
    path('privacy_policy/', privacy, name='privacy-policy'),
    path('terms_of_use/', terms, name='terms-of-use'),
]
