from django.urls import path
from .views import home, features

urlpatterns = [
    path('', home, name='home'),
    path('features/', features, name='features'),
]
