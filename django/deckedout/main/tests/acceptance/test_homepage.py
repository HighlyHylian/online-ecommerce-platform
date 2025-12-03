import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_homepage_loads(client):
    url = reverse("index")
    response = client.get(url)

    assert response.status_code == 200
    assert b"Welcome" in response.content or b"Home" in response.content
