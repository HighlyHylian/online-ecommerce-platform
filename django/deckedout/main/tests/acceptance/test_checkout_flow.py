import pytest
from django.urls import reverse
from main.models import CustomUser, Product, Cart, CartItem, Order
@pytest.mark.django_db
def test_checkout_flow(client):
    buyer = CustomUser.objects.create_user(
        username="buyerX", password="pass1234", banned=False
    )

    seller = CustomUser.objects.create_user(
        username="sellerX", password="pass1234", role="seller", banned=False
    )

    product = Product.objects.create(
        seller=seller,
        name="Widget",
        price=5.00,
        description="test",
        stock=5,
        is_approved=True
    )

    cart = Cart.objects.create(buyer=buyer)
    CartItem.objects.create(cart=cart, product=product, quantity=1)

    client.force_login(buyer)

    response = client.post(reverse("checkout"), {
        "address": "123 Main St",
        "payment_method": "card"
    })

    assert response.status_code in (301, 302)

    # Validate order exists
    order = Order.objects.filter(buyer=buyer).first()
    assert order is not None
    assert order.items.count() == 1

    item = order.items.first()
    assert item.product == product
    assert item.quantity == 1
    assert float(order.amountDue) == float(product.price)
