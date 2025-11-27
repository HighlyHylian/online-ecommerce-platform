# ===========================
# Imports
# ===========================

# Standard library
from decimal import Decimal

# Django imports
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q, Sum, F
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User

# Local app imports
from .models import (
    CustomUser, Product, Order, OrderItem, SellerBalance, 
    Cart, CartItem, RefundRequest
)
from .forms import ProductForm

# ===========================
# Helper Functions / Decorators
# ===========================

def is_buyer(user):
    return hasattr(user, 'role') and user.role == 'buyer'

def buyer_required(view_func):
    decorated_view_func = user_passes_test(
        lambda user: user.is_authenticated and hasattr(user, 'role') and user.role == 'buyer',
        login_url='login'
    )(view_func)
    return decorated_view_func

def seller_required(view_func):
    def check_seller(user):
        return user.is_authenticated and getattr(user, 'role', None) == 'seller'

    decorated_view_func = user_passes_test(
        check_seller,
        login_url='login'
    )(view_func)
    return decorated_view_func

def is_superuser(user):
    return user.is_superuser









# ===========================
# Basic Pages
# ===========================

def home(request):
    return render(request, 'main/index.html')

def about(request):
    return render(request, 'main/about.html')

def skateboards(request):
    products = Product.objects.filter(is_approved=True)
    return render(request, 'main/skateboards.html', {'products': products})

def blog(request):
    return render(request, 'main/blog.html')


# ===========================
# Authentication Views
# ===========================

def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        role = request.POST.get('role')

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


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('admin_dashboard')
            elif user.role == 'seller':
                return redirect('seller_dashboard')
            else:
                return redirect('user_profile')
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('login')

    return render(request, 'main/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# ===========================
# Profile / Dashboard Views
# ===========================

@login_required
@buyer_required
def user_profile(request):
    if request.user.role != 'buyer' or request.user.is_superuser:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('index')  # or wherever you want sellers to go

    return render(request, 'main/user_profile.html')


@seller_required
def seller_dashboard(request):
    seller_products = Product.objects.filter(seller=request.user)
    return render(request, 'main/seller_dashboard.html', {'products': seller_products})


@user_passes_test(is_superuser)
def admin_dashboard(request):
    users = CustomUser.objects.all()
    return render(request, 'main/admin_dashboard.html', {'users': users})


# ===========================
# Product Approval Views
# ===========================

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
@user_passes_test(lambda u: u.is_superuser)
def admin_approve(request):
    products = Product.objects.filter(is_approved=False)
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        product = Product.objects.get(product_id=product_id)
        product.is_approved = True
        product.save()
        return redirect('admin_approve')
    return render(request, 'main/admin_approve.html', {'products': products})


# ===========================
# Product Management Views
# ===========================

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


@login_required
def seller_products(request):
    products = Product.objects.filter(seller=request.user)
    return render(request, 'main/seller_products.html', {'products': products})


@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id, seller=request.user)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            edited_product = form.save(commit=False)
            edited_product.is_approved = False
            edited_product.is_edited = True
            edited_product.save()
            messages.success(request, "Product updated! Waiting for admin approval.")
            return redirect('seller_dashboard')
    else:
        form = ProductForm(instance=product)

    return render(request, 'main/edit_product.html', {'form': form})


@login_required
def update_quantity(request, product_id):
    product = get_object_or_404(Product, pk=product_id, seller=request.user)
    if request.method == "POST":
        try:
            new_quantity = int(request.POST.get("quantity", product.quantity))
            if new_quantity < 0:
                messages.error(request, "Quantity cannot be negative.")
            else:
                product.quantity = new_quantity
                product.save()
                messages.success(request, f"Quantity for {product.name} updated!")
        except ValueError:
            messages.error(request, "Invalid quantity entered.")
    return redirect('seller_dashboard')


# ===========================
# Search
# ===========================

def product_search(request):
    query = request.GET.get('q', '')
    results = []
    if query:
        results = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
    return render(request, 'main/search_results.html', {'query': query, 'results': results})


# ===========================
# Cart & Checkout Views
# ===========================

@login_required
@buyer_required
def add_to_cart(request, product_id):
    if request.user.role != 'buyer' or request.user.is_superuser:
        messages.error(request, "Only buyers can add products to the cart.")
        return redirect('home')

    product = get_object_or_404(Product, product_id=product_id)
    cart, created = Cart.objects.get_or_create(buyer=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f"{product.name} added to cart.")
    return redirect('cart_view')


@login_required
@buyer_required
def cart_view(request):
    # Only buyers can access, thanks to @buyer_required
    if request.user.role != 'buyer' or request.user.is_superuser:
        messages.error(request, "Only buyers can view cart.")
        return redirect('home')

    # Get or create a cart for the buyer
    cart, created = Cart.objects.get_or_create(buyer=request.user)
    cart_items = cart.items.all()  # all CartItem objects related to this cart

    # Calculate total
    total_price = sum(item.subtotal() for item in cart_items)

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'main/cart_view.html', context)


@login_required
@buyer_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, cart__buyer=request.user)
    item.delete()
    messages.info(request, "Item removed from cart.")
    return redirect('cart_view')


@login_required
@buyer_required
def checkout(request):
    if request.user.role != 'buyer':
        messages.error(request, "Only buyers can checkout.")
        return redirect('home')

    cart = get_object_or_404(Cart, buyer=request.user)
    if not cart.items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('cart_view')

    total = cart.total_price()
    order = Order.objects.create(buyer=request.user, amountDue=total)

    for item in cart.items.all():
        product = item.product
        if item.quantity > product.stock:
            messages.error(request, f"Not enough stock for {product.name}.")
            return redirect('cart_view')
        product.stock -= item.quantity
        product.save()
        OrderItem.objects.create(order=order, product=product, quantity=item.quantity, pricePurchased=product.price)
        balance, _ = SellerBalance.objects.get_or_create(seller=product.seller)
        balance.site_balance += product.price * item.quantity
        balance.save()

    cart.items.all().delete()
    messages.success(request, "Order placed successfully!")
    return redirect('buyer_orders')


@login_required
def buyer_orders(request):
    # Block sellers + superusers
    if request.user.role != 'buyer' or request.user.is_superuser:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('index')

    # Get all orders placed by this buyer
    orders = request.user.orders_as_buyer.all().order_by('-created_at')

    # Add a dynamic "reviewed" attribute for each item
    for order in orders:
        for item in order.items.all():
            item.reviewed = item.product.reviews.filter(user=request.user).exists()

    return render(request, 'main/buyer_orders.html', {'orders': orders})



# ===========================
# Seller Financial Views
# ===========================

@seller_required
def seller_orders(request):
    order_items = OrderItem.objects.filter(product__seller=request.user)
    orders = Order.objects.filter(items__in=order_items).distinct()
    return render(request, 'main/seller_orders.html', {'orders': orders})


@seller_required
def claim_balance(request):
    balance, _ = SellerBalance.objects.get_or_create(seller=request.user)
    if request.method == 'POST':
        balance.site_balance = Decimal('0.00')
        balance.save()
        messages.success(request, "Balance claimed successfully!")
    return render(request, 'main/claim_balance.html', {'balance': balance})


@seller_required
def seller_payout(request):
    balance, _ = SellerBalance.objects.get_or_create(seller=request.user)
    if request.method == 'POST':
        claimed_amount = balance.site_balance
        balance.site_balance = Decimal('0.00')
        balance.save()
        messages.success(request, f"You have claimed ${claimed_amount}!")
    return render(request, 'main/seller_payout.html', {'balance': balance})


# ===========================
# Refund Views
# ===========================

@login_required
def request_refund(request, order_item_id):
    order_item = get_object_or_404(OrderItem, id=order_item_id, order__buyer=request.user)
    if RefundRequest.objects.filter(order_item=order_item).exists():
        messages.warning(request, "Refund request already submitted for this item.")
        return redirect('buyer_orders')

    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        if not reason:
            messages.error(request, "Please provide a reason for the refund.")
            return render(request, 'main/request_refund.html', {'order_item': order_item})

        RefundRequest.objects.create(order_item=order_item, buyer=request.user, reason=reason)
        messages.success(request, "Refund request submitted successfully!")
        return redirect('buyer_orders')

    return render(request, 'main/request_refund.html', {'order_item': order_item})


@seller_required
def seller_refunds(request):
    refund_requests = RefundRequest.objects.filter(order_item__product__seller=request.user, status='requested')
    return render(request, 'main/seller_refunds.html', {'refund_requests': refund_requests})


@seller_required
def handle_refund(request, refund_id, action):
    refund = get_object_or_404(RefundRequest, id=refund_id, order_item__product__seller=request.user)
    if action == 'approve':
        refund.status = 'approved'
        messages.success(request, f"Refund for {refund.order_item.product.name} approved.")
    elif action == 'deny':
        refund.status = 'denied'
        messages.warning(request, f"Refund for {refund.order_item.product.name} denied.")
    refund.save()
    return redirect('seller_refunds')

from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Review, Order
from .forms import ReviewForm
from django.contrib.auth.decorators import login_required

# views.py
@login_required
def leave_review(request, order_item_id):
    order_item = get_object_or_404(OrderItem, id=order_item_id, order__buyer=request.user)
    product = order_item.product

    # Prevent reviewing an item twice
    if Review.objects.filter(user=request.user, product=product).exists():
        return redirect('buyer_orders')

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            return redirect('buyer_orders')
    else:
        form = ReviewForm()

    return render(request, 'main/leave_review.html', {'form': form, 'product': product})


from django.db.models import Avg, Count

products = Product.objects.annotate(
    average_rating=Avg('reviews__rating'),
    review_count=Count('reviews')
)
