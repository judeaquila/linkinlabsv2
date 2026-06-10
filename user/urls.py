from django.urls import path
from .views import user_dashboard, profile, tests, request_test, user_requests, transactions, update_test_request, cancel_test_request, pay_now, admin_dashboard, manage_users, edit_user, manage_test_requests, update_delivery_status, transaction_ledger

urlpatterns = [
    path('dashboard/', user_dashboard, name='user_dashboard'),
    path('profile/', profile, name='profile'),
    path('tests/', tests, name='tests'),
    path('request_test/', request_test, name='request_test'),
    path('update_test_request/<str:id>/', update_test_request, name='update_test_request'),
    path('cancel_test_request/<str:id>/', cancel_test_request, name='cancel_test_request'),
    path('all_requests/', user_requests, name='all_requests'),
    path('transactions/', transactions, name='transactions'),
    path('pay_now/<str:id>/', pay_now, name='pay_now'),

    # ADMIN
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin/manage_users/', manage_users, name='manage_users'),
    path('admin/edit_user/<str:id>/', edit_user, name='edit_user'),
    path('admin/manage_test_requests/', manage_test_requests, name='manage_test_requests'),
    path('admin/update_delivery_status/<str:id>/', update_delivery_status, name='update_delivery_status'),
    path('admin/transactions/', transaction_ledger, name='transactions'),
]