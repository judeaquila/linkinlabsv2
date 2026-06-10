from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from accounts.forms import EditUserForm, EditUserProfileForm, EditUserSocialForm
from accounts.models import UserProfile, UserSocial
from .models import Test, TestRequest, UserActivity, TestPrice, User
from .forms import TestRequestForm, TestStatusForm
from django.contrib import messages
from payment.models import Payment, UserWallet
from django.conf import settings
from accounts.decorators import staff_required
from django.db.models import Sum
from django.utils import timezone
from payment.models import Payment

# USER DASHBOARD VIEW
@login_required
def user_dashboard(request):
    # Track Requests
    total_requests = TestRequest.objects.filter(user=request.user).count()
    submitted_requests = TestRequest.objects.filter(user=request.user, delivery_status='Submitted').count()
    dispatched_requests = TestRequest.objects.filter(user=request.user, delivery_status='Dispatched to Lab').count()
    completed_requests = TestRequest.objects.filter(user=request.user, delivery_status='Completed').count()

    # Track User Activities
    user_activities = UserActivity.objects.filter(user=request.user).order_by('-timestamp')[:10]

    context = {
        'user_activities':user_activities,
        'total_requests':total_requests,
        'submitted_requests':submitted_requests,
        'dispatched_requests':dispatched_requests,
        'completed_requests':completed_requests,
    }

    return render(request, 'user/user_dashboard.html', context)

# USER PROFILE VIEW
@login_required
def profile(request):
    # Create User Profile Instance
    try:
        user_profile = request.user.userprofile
        user_social = request.user.usersocial
    except UserProfile.DoesNotExist or UserSocial.DoesNotExist:
        user_profile = UserProfile(user=request.user)
        user_social = UserSocial(user=request.user)
        user_profile.save()
        user_social.save()
    
    # Edit User Form
    if request.method == 'POST':
        user_form = EditUserForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()

            # Create Activity Log
            UserActivity.objects.create(
                user = request.user,
                activity_type = 'User Details Edit',
                description = f"Edited user details."
            )
            messages.success(request, 'User details updated successfully!')

            return redirect('profile')
    else:
        user_form = EditUserForm(instance=request.user)

    # Edit Profile Form
    if request.method == 'POST':
        profile_form = EditUserProfileForm(request.POST, instance=request.user.userprofile)
        if profile_form.is_valid():
            profile_form.save()
            print(profile_form)

            # Create Activity Log
            UserActivity.objects.create(
                user = request.user,
                activity_type = 'User Profile Edit',
                description = f"Edited user profile details."
            )
            messages.success(request, 'Profile details updated successfully!')

            return redirect('profile')
    else:
        profile_form = EditUserProfileForm(instance=request.user.userprofile)

    # Edit Social Media Handles Form
    if request.method == 'POST':
        social_form = EditUserSocialForm(request.POST, instance=request.user.usersocial)
        if social_form.is_valid():
            social_form.save()

            # Create Activity Log
            UserActivity.objects.create(
                user = request.user,
                activity_type = 'User Social Media Handles Edit',
                description = f"Edited user social media handles' details."
            )
            messages.success(request, "Social media handles' details updated successfully!")

            return redirect('profile')
    else:
        social_form = EditUserSocialForm(instance=request.user.usersocial)
    
    context = {
        'user_form':user_form,
        'profile_form':profile_form,
        'social_form':social_form,
    }
    return render(request, 'user/profile.html', context)

# ALL AVAILABLE TESTS VIEW
@login_required
def tests(request):
    # Display FDA & Custom Tests
    fda_gsa_tests = Test.objects.filter(category__name='FDA/GSA Standard Test')
    custom_tests = Test.objects.filter(category__name='Custom Test')

    # Perform Test Request
    if request.method == 'POST':
        form = TestRequestForm(request.POST)

        # Retrieve form data
        if form.is_valid():
            test = form.cleaned_data['test']
            test_category = form.cleaned_data['test_category']
            pricing_option = form.cleaned_data['price_option']
            delivery_method = form.cleaned_data['delivery_method']
            test_price = TestPrice.objects.get(
                test = test,
                category = test_category,
                pricing_option = pricing_option,
            ).price
            
            # Create a new TestRequest instance
            test_request = form.save(commit=False)
            test_request.user = request.user   
            test_request.delivery_status = 'Submitted'
            test_request.price_option = pricing_option
            test_request.test_category = test_category
            test_request.delivery_method = delivery_method
            test_request.test_price = test_price

            test_request.save()

            # Retrieve PayStack Public Key
            pk = settings.PAYSTACK_PUBLIC_KEY

            # Create Payment Instance
            payment = Payment.objects.create(
                amount = test_price,
                email = request.user.email,
                user = request.user,
                test_request = test_request,
            )

            payment.save()

            # Create Activity Log
            UserActivity.objects.create(
                user = request.user,
                activity_type = 'Test Request',
                description = f"Submitted a test request for {test_request.test.name}. Payment not done."
            )
            messages.success(request, 'Test request submitted successfully! Proceed to make payment.')

            context = {
                'payment':payment,
                'paystack_pub_key':pk,
                'amount_value':payment.amount_value,
                'test':test,
            }

            return render(request, 'payment/make_payment.html', context)
    else:
        form = TestRequestForm()

    context = {
        'fda_gsa_tests':fda_gsa_tests,
        'custom_tests':custom_tests,
        'form':form,
    }
    return render(request, 'user/tests.html', context)


# REQUEST FOR LABORATORY TEST
@login_required
def request_test(request):
    if request.method == 'POST':
        form = TestRequestForm(request.POST)

        if form.is_valid():
            test = form.cleaned_data['test']
            test_category = form.cleaned_data['test_category']
            pricing_option = form.cleaned_data['price_option']
            delivery_method = form.cleaned_data['delivery_method']
            
            # Fetch pricing model with defensive lookup handling
            try:
                test_price = TestPrice.objects.get(
                    test=test,
                    category=test_category,
                    pricing_option=pricing_option,
                ).price
            except TestPrice.DoesNotExist:
                messages.error(
                    request, 
                    f"Pricing matrix not found for {test.name} with the selected options. Please modify parameters."
                )
                return render(request, 'user/test_request.html', {'form': form})
            
            # Instantiate and fill the TestRequest object structure
            test_request = form.save(commit=False)
            test_request.user = request.user   
            test_request.delivery_status = 'Submitted'
            test_request.price_option = pricing_option
            test_request.test_category = test_category
            test_request.delivery_method = delivery_method
            test_request.test_price = test_price
            test_request.save()

            # Retrieve PayStack public processing environment variables 
            pk = settings.PAYSTACK_PUBLIC_KEY

            # Instantiate tracking Payment row entry references
            payment = Payment.objects.create(
                amount=test_price,
                email=request.user.email,
                user=request.user,
                test_request=test_request,
            )

            # Record security workflow metrics audit log trails
            UserActivity.objects.create(
                user=request.user,
                activity_type='Test Request',
                description=f"Submitted a test request for {test_request.test.name}. Payment not done."
            )
            
            messages.success(request, 'Test request submitted successfully! Proceed to make payment.')

            context = {
                'payment': payment,
                'paystack_pub_key': pk,
                'amount_value': payment.amount_value,
                'test': test,
            }

            return render(request, 'payment/make_payment.html', context)
            
    else:
        # Check for pre-selection query string context parameters passed from the dashboard
        initial_data = {}
        test_id = request.GET.get('test_id')
        
        if test_id:
            # Safely verify the test actually exists before pre-populating
            test_instance = get_object_or_404(Test, id=test_id)
            initial_data['test'] = test_instance.id

        form = TestRequestForm(initial=initial_data)
    
    context = {
        'form': form,
    }

    return render(request, 'user/test_request.html', context)


# UPDATE TEST REQUEST VIEW
def update_test_request(request, id):
    # Retrieve test request associated with logged in user
    test_request = TestRequest.objects.get(user=request.user, id=id)

    if request.method == 'POST':
        form = TestRequestForm(request.POST, instance=test_request)
        if form.is_valid():
            form.save()

            # Create Activity Log
            UserActivity.objects.create(
                user = request.user,
                activity_type = 'Test Request Update',
                description = f"Updated details for {test_request.test.name} test request."
            )

            messages.success(request, "Test details updated successfully!")
            return redirect('all_requests')
    
    else:
        form = TestRequestForm(instance=test_request)
    context = {
        'form':form,
        'test_request':test_request,
    }
    return render(request, 'user/update_test_request.html', context)

# CANCEL TEST REQUEST VIEW
def cancel_test_request(request, id):
    # Retrieve test request associated with logged in user
    test_request = TestRequest.objects.get(user=request.user, id=id)
    if request.method == 'POST':
        # Create Activity Log
        UserActivity.objects.create(
            user = request.user,
            activity_type = 'Test Request Cancellation',
            description = f"Cancelled {test_request.test.name} test request."
        )
        test_request.delete()
        messages.success(request, "Test request cancelled successfully!")
        return redirect('all_requests')
    context = {'test_request':test_request}
    return render(request, 'user/all_requests.html', context)

# ALL USER REQUESTS VIEW
@login_required
def user_requests(request):
    test_requests = TestRequest.objects.filter(user=request.user).order_by('-date_updated')

    context = {'test_requests':test_requests}
    return render(request, 'user/all_requests.html', context)

# PAY FOR UNPAID TESTS VIEW
@login_required
def pay_now(request, id):
    # Retrieve the unpaid test request
    unpaid_test = get_object_or_404(TestRequest, user=request.user, id=id)

    # Check if the test request is unpaid
    if unpaid_test.payment_status == 'Unpaid':
        # Retrieve TestPrice instance
        test_price = TestPrice.objects.get(
            test = unpaid_test.test,
            category = unpaid_test.test_category,
            pricing_option = unpaid_test.price_option,
        ).price
                    
        # Retrieve PayStack Public Key
        pk = settings.PAYSTACK_PUBLIC_KEY

        # Create a Payment instance
        payment = Payment.objects.create(
            amount=test_price,
            email=request.user.email,
            user=request.user,
            test_request=unpaid_test,
        )

        # Save the payment instance
        payment.save()

        # Prepare context for rendering the payment page
        context = {
            'payment': payment,
            'paystack_pub_key': pk,
            'amount_value': payment.amount_value,
            'test': unpaid_test.test,
        }

        return render(request, 'payment/make_payment.html', context)
    else:
        # If the test request is already paid, redirect to the dashboard or show a message
        messages.info(request, 'This test has already been paid for.')
        return redirect('all_requests')


# USER TRANSACTIONS VIEW
@login_required
def transactions(request):
    # Create Wallet Instance
    try:
        user_wallet = UserWallet.objects.get(user=request.user)
    except UserWallet.DoesNotExist:
        user_wallet = None
    
    # Show transactions related to logged in user only
    payments = Payment.objects.filter(user=request.user)

    context = {
        'user_wallet':user_wallet,
        'payments':payments,
    }
    return render(request, 'user/transactions.html', context)



# ------------------------------------------------------------------------------------------------ #
# ------------------------------ ADMINISTRATOR VIEW LOGIC ---------------------------------------- #
# ------------------------------------------------------------------------------------------------ #
@login_required
@staff_required
def admin_dashboard(request):
    # Setup timezone anchor for the current monthly phase
    now = timezone.now()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Core System Metrics
    users = User.objects.filter(is_superuser=False).count()
    tests_submitted = TestRequest.objects.all().count()
    tests_completed = TestRequest.objects.filter(delivery_status="Completed").count()
    tests_dispatched = TestRequest.objects.filter(delivery_status="Dispatched to Lab").count()

    # Refactored Financial Metrics based on your Payment Model schema
    # 1. Total revenue aggregated across all successfully verified records
    total_revenue = Payment.objects.filter(verified=True).aggregate(total=Sum('amount'))['total'] or 0
    
    # 2. Verified revenue isolated inside this calendar month window
    current_month_revenue = Payment.objects.filter(
        verified=True, 
        date_created__gte=start_of_month
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # 3. Value of unverified attempts/pending settlements currently logged
    pending_payments = Payment.objects.filter(verified=False).aggregate(total=Sum('amount'))['total'] or 0

    # Operational Logs Pipeline
    user_activities = UserActivity.objects.all().order_by('-timestamp')[:10]

    context = {
        'users': users,
        'tests_submitted': tests_submitted,
        'tests_completed': tests_completed,
        'tests_dispatched': tests_dispatched,
        'total_revenue': total_revenue,
        'current_month_revenue': current_month_revenue,
        'pending_payments': pending_payments,
        'user_activities': user_activities,
    }
    return render(request, 'admin/admin_dashboard.html', context)


@staff_required
@login_required
def manage_users(request):
    users = User.objects.filter(is_superuser=False, is_staff=False)
    user_profiles = UserProfile.objects.filter(user__in=users)
    context = {
        'users': users,
        'user_profiles': user_profiles,
    }
    return render(request, 'admin/manage_users.html', context)


@staff_required
@login_required
def edit_user(request, id):
    user = User.objects.get(id=id)
    if request.method == 'POST':
        form = EditUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()

        # Create Activity Log
        UserActivity.objects.create(
            user = request.user,
            activity_type = 'Update User Details',
            description = f"updated {user.username}'s details in the database."
        )
        messages.success(request, 'User details updated successfully!')
        return redirect('manage_users')
    else:
        form = EditUserForm(instance=user)

    context = {
        'user':user,
        'form':form,
    }
    return render(request, 'admin/edit_user.html', context)


@staff_required
@login_required
def delete_user(request, id):
    user = User.objects.get(id=id)
    if request.method == 'POST':
        # Create Activity Log
        UserActivity.objects.create(
            user = request.user,
            activity_type = 'Delete User',
            description = f"deleted {user.username} from database"
        )
        user.delete()
        messages.success(request, "User deleted successfully!")
        return redirect('manage_users')


@staff_required
@login_required
def manage_test_requests(request):
    all_requests = TestRequest.objects.all().order_by('-date_updated')
    context = {
        'all_requests':all_requests,
    }
    return render(request, 'admin/manage_test_requests.html', context)


@staff_required
@login_required
def update_delivery_status(request, id):
    # Retrieve test request associated with delivery status
    test_request = TestRequest.objects.get(id=id)

    if request.method == 'POST':
        form = TestStatusForm(request.POST, instance=test_request)
        if form.is_valid():
            form.save()

            messages.success(request, "Test details updated successfully!")
            return redirect('manage_test_requests')
    
    else:
        form = TestStatusForm(instance=test_request)
    context = {
        'form':form,
        'test_request':test_request,
    }
    return render(request, 'admin/update_delivery_status.html', context)


@login_required
@staff_required
def transaction_ledger(request):
    # Fetching payments with user context to optimize database hits
    transactions = Payment.objects.select_related('user').order_by('-date_created')
    
    # Simple calculation for a secondary summary line
    total_volume = transactions.filter(verified=True).aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'transactions': transactions,
        'total_volume': total_volume,
    }
    return render(request, 'admin/revenue_ledger.html', context)