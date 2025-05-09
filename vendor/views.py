from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, LoginForm
from .models import VendorProfile, User

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            if user.is_vendor:
                return redirect('vendor_dashboard')
            return redirect('client_bookings')
    else:
        form = RegisterForm()
    return render(request, 'vendor/auth_form.html', {'form': form, 'mode': 'register'})

def login_view(request):
    # 1) Determine the post‑login destination
    #   Prefer ?next= from GET, then from POST hidden field, else None
    next_url = request.GET.get('next') or request.POST.get('next')

    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # 2) Redirect to next_url if supplied
            if next_url:
                return redirect(next_url)

            # 3) Otherwise fall back to role homepages
            if user.is_vendor:
                return redirect('vendor_dashboard')
            if user.is_client:
                return redirect('client_bookings')
            return redirect('home')
    else:
        form = LoginForm()

    # 4) Render the form, passing next_url so the template can include it
    return render(request, 'vendor/auth_form.html', {
        'form': form,
        'mode': 'login',
        'next': next_url,
    })

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def vendor_dashboard(request):
    if not request.user.is_vendor:
        return redirect('login_vendor')
    vendor = request.user.vendor_profile
    return render(request, 'vendor/dashboard.html', {'vendor': vendor})

def logout_user(request):
    logout(request)
    return redirect('login_vendor')
