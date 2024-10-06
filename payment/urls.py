from django.urls import path
from .views import initiate_deposit, verify_payment, verify_deposit

urlpatterns = [
    path('initiate_deposit/', initiate_deposit, name='initiate_deposit'),
    path('verify_deposit/<str:ref>/', verify_deposit, name="verify_deposit"),
    path('verify_payment/<str:ref>/', verify_payment, name="verify_payment"),
]
