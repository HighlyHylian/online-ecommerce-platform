import pytest
from django.urls import reverse
from main.models import CustomUser

@pytest.mark.django_db
def test_buyer_login(client):
    buyer = CustomUser.objects.create_user(
        username="buyer1",
        password="pass123",
        role="buyer",
        banned=False
    )

    response = client.post(reverse("login"), {
        "username": "buyer1",
        "password": "pass123"
    })

    assert response.status_code in (301, 302)
    assert "_auth_user_id" in client.session
    assert client.session["_auth_user_id"] == str(buyer.id)


@pytest.mark.django_db
def test_seller_login(client):
    seller = CustomUser.objects.create_user(
        username="seller1",
        password="pass123",
        role="seller",
        banned=False
    )

    response = client.post(reverse("login"), {
        "username": "seller1",
        "password": "pass123"
    })

    assert response.status_code in (301, 302)
    assert "_auth_user_id" in client.session
    assert client.session["_auth_user_id"] == str(seller.id)
