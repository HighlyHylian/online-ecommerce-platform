import pytest
from django.urls import reverse
from main.models import CustomUser, Product, Review

@pytest.mark.django_db
def test_buyer_can_review_product(client):
    seller = CustomUser.objects.create_user(
        username="sellerY", password="pass", role="seller", banned=False
    )
    buyer = CustomUser.objects.create_user(
        username="buyerY", password="pass", role="buyer", banned=False
    )

    product = Product.objects.create(
        seller=seller,
        name="Cool Item",
        price=10.00,
        description="desc",
        stock=10,
        is_approved=True
    )

    client.force_login(buyer)

    response = client.post(reverse("leave_review", args=[product.product_id]), {
        "rating": 4,
        "comment": "Great product!"
    })

    assert response.status_code in (302, 301)
    assert Review.objects.count() == 1

    review = Review.objects.first()
    assert review.user == buyer
    assert review.product == product
    assert review.rating == 4
    assert review.comment == "Great product!"


@pytest.mark.django_db
def test_seller_cannot_review_own_product(client):
    seller = CustomUser.objects.create_user(
        username="sellerZ", password="pass", role="seller", banned=False
    )

    product = Product.objects.create(
        seller=seller,
        name="Seller Item",
        price=10.00,
        description="desc",
        stock=10,
        is_approved=True
    )

    client.force_login(seller)

    response = client.post(reverse("leave_review", args=[product.product_id]), {
        "rating": 5,
        "comment": "My own product!"
    })

    assert response.status_code in (403, 302, 301)
    assert Review.objects.count() == 0


@pytest.mark.django_db
def test_product_average_rating():
    seller = CustomUser.objects.create_user(
        username="sellerR", password="pass", role="seller", banned=False
    )
    buyer = CustomUser.objects.create_user(
        username="buyerR", password="pass", banned=False
    )
    product = Product.objects.create(
        seller=seller,
        name="Rated Item",
        price=5,
        description="desc",
        stock=5,
        is_approved=True
    )

    Review.objects.create(product=product, user=buyer, rating=5)
    Review.objects.create(product=product, user=buyer, rating=3)

    assert product.average_rating() == 4.0
    assert product.review_count() == 2
