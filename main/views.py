from django.shortcuts import render

# LANDING PAGE
def home(request):
    return render(request, 'main/index.html')

# FEATURES PAGE
def features(request):
    return render(request, 'main/features.html')