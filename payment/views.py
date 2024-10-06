from django.shortcuts import render, redirect
from .models import Payment, UserWallet
from django.conf import settings
from django.http import Http404
from .forms import CardPaymentForm
from django.contrib import messages
from user.models import UserActivity

# Create your views here.
def initiate_deposit(request):
    if request.method == 'POST':
        form = CardPaymentForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']

            pk = settings.PAYSTACK_PUBLIC_KEY

            payment = Payment.objects.create(
                amount = amount,
                email = request.user.email,
                user = request.user
            )

            payment.save()

            context = {
                'payment':payment,
                'paystack_pub_key':pk,
                'amount_value':payment.amount_value,
            }

            return render(request, 'payment/make_deposit.html', context)

    else:
        form = CardPaymentForm()

    context = {
        'form':form,
    }

    return render(request, 'payment/deposit.html', context)


def verify_deposit(request, ref):
    try:
        payment = Payment.objects.get(ref=ref)
    except Payment.DoesNotExist:
        raise Http404("Payment does not exist.")

    verified = payment.verify_deposit()

    if verified:
        try:
            user_wallet = UserWallet.objects.get(user=request.user)
        except UserWallet.DoesNotExist:
            # Create a new UserWallet if it doesn't exist
            user_wallet = UserWallet.objects.create(user=request.user, balance=0)
        
        user_wallet.balance += payment.amount
        user_wallet.save()

        # Create Activity Log
        UserActivity.objects.create(
            user = request.user,
            activity_type = 'Wallet Deposit',
            description = f"Made a deposit of GHS {payment.amount}."
        )
        messages.success(request, f'Successfully deposited GHS {payment.amount} into wallet.')
        
        return render(request, "payment/success.html", {'message': 'Wallet funded successfully!'})
    
    return render(request, "payment/success.html", {'message': 'Payment verification failed.'})

def verify_payment(request, ref):
    try:
        payment = Payment.objects.get(ref=ref)
    except Payment.DoesNotExist:
        raise Http404("Payment does not exist.")

    verified = payment.verify_payment()

    if verified:
        test_request = payment.test_request
        test_request.payment_status = 'Paid'
        test_request.save()
        
        # Create Activity Log
        UserActivity.objects.create(
            user = request.user,
            activity_type = 'Payment made',
            description = f"Made a payment of GHS {payment.amount} for test request."
        )
        messages.success(request, f'Successfully made payment of GHS {payment.amount} for test request.')
        return redirect('user_dashboard')
    else:
        messages.error(request, "Payment verification failed.")
        return redirect('user_dashboard')