from django.urls import path
from .views import sign_up, custom_login

urlpatterns = [
    path('register/', sign_up, name='register'),
    path('login/', custom_login, name='login'),
]
