from django.shortcuts import render, redirect
from django.contrib.auth.models import User

from .models import CustomUser

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Product
from django.db.models import Q

from .models import Product, Order, OrderItem, SellerBalance

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

from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # or email if you use email login
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.banned:  # 🔹 Block banned users
                messages.error(request, 'Your account has been banned. Please contact support.')
                return redirect('login')

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

from django.shortcuts import get_object_or_404, redirect

@user_passes_test(is_superuser)
def toggle_ban(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.banned = not user.banned
    user.save()
    return redirect('admin_dashboard')






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

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

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

from decimal import Decimal
@login_required
def checkout(request):
    cart = request.session.get('cart', {})  # Example: {'1': 2, '3': 1}
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('cart')

    order = Order.objects.create(buyer=request.user)
    total_price = Decimal('0.00')

    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)

        # Prevent overselling
        if product.stock < quantity:
            messages.error(request, f"Not enough stock for {product.name}.")
            order.delete()
            return redirect('cart')

        # Create order item
        order_item = OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=product.price
        )

        # Update totals
        total_price += product.price * quantity

        # Decrease stock
        product.stock -= quantity
        product.save()

        # Update seller's site balance
        seller_balance, _ = SellerBalance.objects.get_or_create(seller=product.seller)
        seller_balance.site_balance += product.price * quantity
        seller_balance.save()

    order.total_price = total_price
    order.save()

    # Clear the cart
    request.session['cart'] = {}

    messages.success(request, "Order placed successfully!")
    return redirect('buyer_orders')


@login_required
def seller_orders(request):
    if request.user.role != 'seller':
        # optional: redirect non-sellers
        return redirect('home')

    # Get all OrderItems for products belonging to this seller
    order_items = OrderItem.objects.filter(product__seller=request.user)

    # Get unique orders from those order items
    orders = Order.objects.filter(items__in=order_items).distinct()

    context = {
        'orders': orders,
    }
    return render(request, 'main/seller_orders.html', context)





@login_required
def claim_balance(request):
    balance, _ = SellerBalance.objects.get_or_create(seller=request.user)

    if request.method == 'POST':
        balance.site_balance = Decimal('0.00')
        balance.save()
        messages.success(request, "Balance claimed successfully!")

    return render(request, 'main/claim_balance.html', {'balance': balance})



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Cart, CartItem, Order, OrderItem, SellerBalance
@login_required
def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')

    product = get_object_or_404(Product, pk=product_id)
    quantity = int(request.POST.get('quantity', 1))

    # Get or create cart for this user
    cart, created = Cart.objects.get_or_create(buyer=request.user)

    # Check if the product already exists in cart
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
    cart_item.save()

    return redirect(request.META.get('HTTP_REFERER', 'skateboards'))



from django.shortcuts import render, get_object_or_404, redirect
from .models import Cart, CartItem, Product
@login_required
def cart_view(request):
    if request.user.is_authenticated:
        # Get or create a cart for the user
        cart, created = Cart.objects.get_or_create(buyer=request.user)
        cart_items = cart.items.all()  # all CartItem objects related to this cart

        total_price = sum(item.subtotal() for item in cart_items)
    else:
        cart_items = []
        total_price = 0

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'main/cart_view.html', context)



@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, cart__buyer=request.user)
    item.delete()
    messages.info(request, "Item removed from cart.")
    return redirect('cart_view')






@login_required
def checkout(request):
    cart = get_object_or_404(Cart, buyer=request.user)

    if not cart.items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('cart_view')

    # Create Order
    total = cart.total_price()
    order = Order.objects.create(buyer=request.user, amountDue=total)

    for item in cart.items.all():
        product = item.product
        if item.quantity > product.stock:
            messages.error(request, f"Not enough stock for {product.name}.")
            return redirect('cart_view')

        # Reduce stock
        product.stock -= item.quantity
        product.save()

        # Create order item
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=item.quantity,
            pricePurchased=product.price
        )

        # Update seller balance
        balance, _ = SellerBalance.objects.get_or_create(seller=product.seller)
        balance.site_balance += product.price * item.quantity
        balance.save()

    # Clear cart
    cart.items.all().delete()

    messages.success(request, "Order placed successfully!")
    return redirect('buyer_orders')  # or any confirmation page



@login_required
def buyer_orders(request):
    orders = request.user.orders_as_buyer.all().order_by('-created_at')  # newest first
    return render(request, 'main/buyer_orders.html', {'orders': orders})

    return render(request, 'main/cart_view.html', {'cart_items': cart_items, 'total': total})

from django.db.models import Sum, F

@login_required
def seller_payout(request):
    if request.user.role != 'seller':
        messages.error(request, "You are not authorized to access this page.")
        return redirect('home')

    balance, _ = SellerBalance.objects.get_or_create(seller=request.user)

    if request.method == 'POST':
        claimed_amount = balance.site_balance
        balance.site_balance = Decimal('0.00')
        balance.save()
        messages.success(request, f"You have claimed ${claimed_amount}!")

    return render(request, 'main/seller_payout.html', {'balance': balance})


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import OrderItem, RefundRequest

@login_required
def request_refund(request, order_item_id):
    order_item = get_object_or_404(OrderItem, id=order_item_id, order__buyer=request.user)

    # Check if a refund request already exists
    if RefundRequest.objects.filter(order_item=order_item).exists():
        messages.warning(request, "Refund request already submitted for this item.")
        return redirect('buyer_orders')

    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        if not reason:
            messages.error(request, "Please provide a reason for the refund.")
            return render(request, 'main/request_refund.html', {'order_item': order_item})
        
        RefundRequest.objects.create(
            order_item=order_item,
            buyer=request.user,
            reason=reason
        )
        messages.success(request, "Refund request submitted successfully!")
        return redirect('buyer_orders')

    return render(request, 'main/request_refund.html', {'order_item': order_item})



@login_required
def handle_refund(request, item_id, action):
    item = get_object_or_404(OrderItem, id=item_id, product__seller=request.user)

    if item.refund_status == 'requested':
        if action == 'approve':
            item.refund_status = 'approved'
            # You can also adjust seller.site_balance -= item.subtotal() here
            item.save()
            messages.success(request, f"Refund approved for {item.product.name}.")
        elif action == 'deny':
            item.refund_status = 'denied'
            item.save()
            messages.warning(request, f"Refund denied for {item.product.name}.")
    else:
        messages.info(request, f"Refund for {item.product.name} already {item.refund_status}.")

    return redirect('main/seller_refunds')


@login_required
def seller_refunds(request):
    refund_requests = OrderItem.objects.filter(product__seller=request.user, refund_status='requested')
    return render(request, 'main/seller_refunds.html', {'refund_requests': refund_requests})
