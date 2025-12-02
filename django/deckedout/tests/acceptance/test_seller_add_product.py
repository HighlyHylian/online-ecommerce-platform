import pytest
from django.urls import reverse
from main.models import CustomUser, Product

@pytest.mark.django_db
def test_seller_can_add_product(client):
    seller = CustomUser.objects.create_user(
        username="sellerX",
        password="sellerpass",
        role="seller",
        banned=False
    )

    client.force_login(seller)

    response = client.post(reverse("add_product"), {
        "name": "Test Product",
        "price": "9.99",
        "description": "A great product",
        "stock": 5,
        "is_approved": True,
    })

    assert response.status_code in (302, 301)
    assert Product.objects.count() == 1

    product = Product.objects.first()
    assert product.seller == seller
    assert product.name == "Test Product"


@pytest.mark.django_db
def test_buyer_cannot_add_product(client):
    buyer = CustomUser.objects.create_user(
        username="buyerZ",
        password="buyerpass",
        role="buyer",
        banned=False
    )

    client.force_login(buyer)

    response = client.post(reverse("add_product"), {
        "name": "Should Fail",
        "price": "19.99",
        "description": "Nope",
        "stock": 2
    })

    # Expect forbidden or redirect — adjust based on your view logic
    assert response.status_code in (403, 302, 301)
    assert Product.objects.count() == 0
