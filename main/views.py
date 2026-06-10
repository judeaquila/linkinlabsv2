from django.shortcuts import render

# LANDING PAGE
def home(request):
    return render(request, 'main/index.html')

# PRIVACY POLICY
def privacy(request):
    return render(request, 'main/privacy_policy.html')

# TERMS OF USE
def terms(request):
    return render(request, 'main/terms_of_use.html')