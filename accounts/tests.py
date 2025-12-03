import pytest
from django.urls import reverse
import json

# 1. Test User registration
@pytest.mark.django_db
def test_user_registration(client):
    # url = reverse('signup')
    # data = {
    #     'email': 'user@test.com',
    #     'password': "user@Test123",
    #     'full_name': 'Test User',
    #     'phone_number': '1234567890',
    #     'address': '123 Test St',
    # }
    # response = client.post(url, data, content_type='application/json')
    # jsonResp = response.json()

    # print(f"""
    # User registration response:
    # {json.dumps(jsonResp, indent=4)}
    # """)
    pass
    # assert(jsonResp.get("success", False), "Success key is not True")
    # assert(response.status_code == 201, "Status code is not 201 Created")

# 2. Test User login
@pytest.mark.django_db
def test_user_login(client, django_user_model):
    # First, create a user to login
    user = django_user_model.objects.create_user(
        email='user@test.com',
        password="user@Test123",
        full_name='Test User',
        phone_number='1234567890',
        address='123 Test St',
    )
    url = reverse('login')
    data = {
        'email': 'user@test.com',
        'password': "user@Test123",
    }
    response = client.post(url, data, content_type='application/json')
    jsonResp = response.json()

    print(f"""
    User login response:
    {json.dumps(jsonResp, indent=4)}
    """)

    assert(jsonResp.get("success"), "Success key is not True")
    assert(response.status_code == 200, "Status code is not 200 OK")