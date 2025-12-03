import pytest
from django.urls import reverse
from main.models import CustomUser, Product, Cart, CartItem

@pytest.mark.django_db
def test_add_item_to_cart(client):
    # Create a buyer
    buyer = CustomUser.objects.create_user(
        username="buyer1", password="pass1234", banned=False
    )

    # Create a seller
    seller = CustomUser.objects.create_user(
        username="seller1", password="pass1234", role="seller", banned=False
    )

    # Create a product
    product = Product.objects.create(
        seller=seller,
        name="Test Product",
        price=9.99,
        description="test",
        stock=10,
        is_approved=True
    )

    # Create buyer cart
    cart = Cart.objects.create(buyer=buyer)

    client.force_login(buyer)

    # Simulate the "add to cart" endpoint
    url = reverse("add_to_cart", args=[product.product_id])
    response = client.post(url, {"quantity": 1})

    assert response.status_code in (301, 302)
    assert cart.items.count() == 1

    item = cart.items.first()
    assert item.product == product
    assert item.quantity == 1
