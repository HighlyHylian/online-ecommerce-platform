from django.shortcuts import render, redirect
from django.contrib.auth.models import User

from .models import CustomUser

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

# --- Basic Pages ---

def home(request):
    return render(request, 'main/index.html')

def about(request):
    return render(request, 'main/about.html')

def skateboards(request):
    return render(request, 'main/skateboards.html')

# --- Auth Pages ---

def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        role = request.POST.get('role')  # new

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('signup')

        user = CustomUser.objects.create_user(username=username, password=password, role=role)
        user.save()
        messages.success(request, "Account created successfully! Please log in.")
        return redirect('login')

    return render(request, 'main/signup.html')


'''def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.role == 'seller':
                return redirect('seller_dashboard')
            else:
                return redirect('user_profile')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'main/login.html')'''

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # or email if you use email login
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # 🔹 Redirect based on user type
            if user.is_superuser:
                return redirect('admin_dashboard')
            elif user.role == 'seller':
                return redirect('seller_dashboard')  # if you have one
            else:
                return redirect('user_profile')  # or your buyer dashboard

        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('login')

    return render(request, 'main/login.html')



def logout_view(request):
    logout(request)
    return redirect('login')

from django.contrib.auth.decorators import login_required

@login_required
def user_profile(request):
    return render(request, 'main/user_profile.html')

from django.contrib.auth.decorators import login_required

@login_required
def seller_dashboard(request):
    return render(request, 'main/seller_dashboard.html')


from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from .models import CustomUser

def is_superuser(user):
    return user.is_superuser

@user_passes_test(is_superuser)
def admin_dashboard(request):
    users = CustomUser.objects.all()
    return render(request, 'main/admin_dashboard.html', {'users': users})
