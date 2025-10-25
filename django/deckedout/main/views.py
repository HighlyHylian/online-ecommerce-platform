from django.shortcuts import render, redirect
from django.contrib.auth.models import User

from .models import CustomUser

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Product
from django.db.models import Q

from .forms import ProductForm


# --- Basic Pages ---

def home(request):
    return render(request, 'main/index.html')

def about(request):
    return render(request, 'main/about.html')

def skateboards(request):
    products = Product.objects.filter(is_approved=True)
    return render(request, 'main/skateboards.html', {'products': products})
def blog(request):
    return render(request, 'main/blog.html')

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
    # Get only products added by the logged-in seller
    seller_products = Product.objects.filter(seller=request.user)
    
    return render(request, 'main/seller_dashboard.html', {
        'products': seller_products
    })

from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from .models import CustomUser

def is_superuser(user):
    return user.is_superuser

@user_passes_test(is_superuser)
def admin_dashboard(request):
    users = CustomUser.objects.all()
    return render(request, 'main/admin_dashboard.html', {'users': users})





from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def approve_products(request):
    products = Product.objects.filter(is_approved=False)
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = Product.objects.get(pk=product_id)
        product.is_approved = True
        product.is_edited = True
        product.save()
    return render(request, 'admin_approve.html', {'products': products})

@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            messages.success(request, "Product submitted for admin approval!")
            return redirect('seller_dashboard')
    else:
        form = ProductForm()
    return render(request, 'main/add_product.html', {'form': form})


    

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Product


# Restrict to admin/superuser only
@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_approve(request):
    # Get all products waiting for approval
    products = Product.objects.filter(is_approved=False)

    if request.method == "POST":
        product_id = request.POST.get("product_id")
        product = Product.objects.get(product_id=product_id)
        product.is_approved = True
        product.save()
        return redirect('admin_approve')

    return render(request, 'main/admin_approve.html', {'products': products})



from django.shortcuts import get_object_or_404

@login_required
def seller_products(request):
    # Get only the products belonging to the logged-in seller
    products = Product.objects.filter(seller=request.user)
    return render(request, 'main/seller_products.html', {'products': products})


from django.shortcuts import get_object_or_404

@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id, seller=request.user)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            edited_product = form.save(commit=False)
            edited_product.is_approved = False  # need re-approval
            edited_product.is_edited = True
            edited_product.save()
            messages.success(request, "Product updated! Waiting for admin approval.")
            return redirect('seller_dashboard')
    else:
        form = ProductForm(instance=product)

    return render(request, 'main/edit_product.html', {'form': form})



#----------product search functionality-----------


def product_search(request):
    query = request.GET.get('q', '')
    results = []

    if query:
        results = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )

    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'main/search_results.html', context)
