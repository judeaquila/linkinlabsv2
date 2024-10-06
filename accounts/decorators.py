from django.http import HttpResponseRedirect
from django.urls import reverse
from functools import wraps
from django.shortcuts import redirect

# RESTRICT PAGES BASED ON USER ACCESS LEVEL
def staff_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('permission_denied'))
    return _wrapped_view

# RESTRICT ACCESS TO LOGIN PAGE FOR LOGGED IN USERS
def anonymous_required(user_redirect, admin_redirect):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                if request.user.is_staff or request.user.is_superuser:
                    return redirect(admin_redirect)
                else:
                    return redirect(user_redirect)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator