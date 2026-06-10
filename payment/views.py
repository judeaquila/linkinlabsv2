from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from django.conf import settings
from django.db import transaction
from .forms import CardPaymentForm
from .models import Payment, UserWallet
from user.models import UserActivity

@login_required
def initiate_deposit(request):
    if request.method == 'POST':
        form = CardPaymentForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            pk = settings.PAYSTACK_PUBLIC_KEY

            payment = Payment.objects.create(
                amount=amount,
                email=request.user.email,
                user=request.user
            )

            context = {
                'payment': payment,
                'paystack_pub_key': pk,
                'amount_value': payment.amount_value,
            }
            return render(request, 'payment/make_deposit.html', context)
    else:
        form = CardPaymentForm()

    context = {
        'form': form,
    }
    return render(request, 'payment/deposit.html', context)


@login_required
def verify_deposit(request, ref):
    payment = get_object_or_404(Payment, ref=ref)
    
    # --- IDEMPOTENCY GUARD ---
    # Check if this database payment record has already been successfully verified.
    # Note: If your model uses a custom status field (e.g. payment.status == 'success'), use that here instead.
    if getattr(payment, 'verified', False) == True:
        return render(request, "payment/success.html", {
            'message': 'This wallet deposit has already been safely processed and credited.'
        })

    # Call your internal Paystack verification script wrapper
    verified = payment.verify_deposit()

    if verified:
        # Wrap database operations in an atomic transaction to avoid race conditions
        with transaction.atomic():
            # Re-fetch and lock the payment record to double-check state inside the transaction block
            payment.refresh_from_db()
            if getattr(payment, 'verified', False) == True:
                return render(request, "payment/success.html", {'message': 'Wallet funded successfully!'})

            # 1. Update your User Wallet balances
            user_wallet, created = UserWallet.objects.get_or_create(user=request.user, defaults={'balance': 0})
            user_wallet.balance += payment.amount
            user_wallet.save()

            # 2. Mark this transaction row as verified in your DB immediately
            if hasattr(payment, 'verified'):
                payment.verified = True
            elif hasattr(payment, 'status'):
                payment.status = 'success'
            payment.save()

            # 3. Log Activity
            UserActivity.objects.create(
                user=request.user,
                activity_type='Wallet Deposit',
                description=f"Made a deposit of GHS {payment.amount}."
            )
            
            messages.success(request, f'Successfully deposited GHS {payment.amount} into wallet.')
            return render(request, "payment/success.html", {'message': 'Wallet funded successfully!'})
    
    return render(request, "payment/success.html", {'message': 'Payment verification failed.'})


@login_required
def verify_payment(request, ref):
    payment = get_object_or_404(Payment, ref=ref)
    test_request = payment.test_request
    test_name = test_request.test.name

    # --- IDEMPOTENCY GUARD ---
    # Check if the associated test request has already been set to 'Paid'
    if test_request.payment_status == 'Paid':
        messages.info(request, f"Payment for {test_name} has already been verified.")
        return redirect('user_dashboard')

    # Call your internal Paystack verification script wrapper
    verified = payment.verify_payment()

    if verified:
        with transaction.atomic():
            # Re-fetch test request inside the database transaction block
            test_request.refresh_from_db()
            if test_request.payment_status == 'Paid':
                return redirect('user_dashboard')

            # 1. Secure status assignment
            test_request.payment_status = 'Paid'
            test_request.save()

            # 2. Mark payment model entry closed
            if hasattr(payment, 'verified'):
                payment.verified = True
            elif hasattr(payment, 'status'):
                payment.status = 'success'
            payment.save()
            
            # 3. Log Activity
            UserActivity.objects.create(
                user=request.user,
                activity_type='Payment made',
                description=f"Made a payment of GHS {payment.amount} for {test_name} test request."
            )
            
            messages.success(request, f'Successfully made payment of GHS {payment.amount} for {test_name} test request.')
            return redirect('user_dashboard')
    else:
        # Explicitly tag as failed locally to kill repeating hooks
        if hasattr(payment, 'status'):
            payment.status = 'failed'
            payment.save()
            
        messages.error(request, "Payment verification failed.")
        return redirect('user_dashboard')