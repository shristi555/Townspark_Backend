import pytest
import json
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from issue.models import Category, Issue
from progress.models import Progress

User = get_user_model()


@pytest.fixture
def api_client():
    """Return an API client instance."""
    return APIClient()


@pytest.fixture
def create_user(db):
    """Factory fixture to create users."""
    def make_user(email, password, **kwargs):
        user = User.objects.create_user(email=email, password=password, **kwargs)
        return user
    return make_user


@pytest.fixture
def regular_user(db, create_user):
    """Create a regular user."""
    return create_user(
        email="user@test.com",
        password="user@Test123",
        full_name="Regular User",
        phone_number="+1234567890",
        address="123 Test Street"
    )


@pytest.fixture
def another_user(db, create_user):
    """Create another regular user."""
    return create_user(
        email="another@test.com",
        password="another@Test123",
        full_name="Another User"
    )


@pytest.fixture
def category(db):
    """Create a test category."""
    return Category.objects.create(
        name="Potholes",
        description="Issues related to potholes on roads."
    )


@pytest.fixture
def issue(db, category, regular_user):
    """Create a test issue."""
    return Issue.objects.create(
        title="Test Pothole",
        description="There is a large pothole on Main St.",
        location="Main St. near 1st Ave.",
        category=category,
        reported_by=regular_user
    )


@pytest.fixture
def progress(db, issue, regular_user):
    """Create a test progress update."""
    return Progress.objects.create(
        issue=issue,
        description="Started working on the pothole.",
        updated_by=regular_user
    )


@pytest.mark.django_db
class TestMyProfile:
    """Test cases for my profile endpoint."""

    def test_get_my_profile(self, api_client, regular_user, issue, progress):
        """
        Test retrieving authenticated user's profile.
        
        Scenario:
        1. Authenticate as user.
        2. Get my profile.
        3. Verify user info, issues_reported count, and progress_updates count.
        """
        api_client.force_authenticate(user=regular_user)
        
        response = api_client.get("/api/v1/accounts/profile/mine/")
        
        print(f"\nMy profile response:")
        print(json.dumps(response.json(), indent=4))
        
        assert response.status_code == 200
        
        json_resp = response.json()
        assert json_resp.get("success") == True
        
        profile_data = json_resp.get("response", {}).get("user", {})
        assert profile_data.get("id") == regular_user.id
        assert profile_data.get("email") == regular_user.email
        assert profile_data.get("full_name") == regular_user.full_name
        assert profile_data.get("issues_reported") == 1
        assert profile_data.get("progress_updates") == 1
        assert len(profile_data.get("issues", [])) == 1

    def test_get_my_profile_without_auth(self, api_client):
        """Test that unauthenticated users cannot get profile."""
        response = api_client.get("/api/v1/accounts/profile/mine/")
        
        print(f"\nUnauthenticated profile response:")
        print(json.dumps(response.json(), indent=4))
        
        assert response.status_code == 401


@pytest.mark.django_db
class TestUserProfile:
    """Test cases for user profile endpoint."""

    def test_get_user_profile(self, api_client, regular_user, another_user, issue):
        """
        Test retrieving another user's profile.
        
        Scenario:
        1. Authenticate as another_user.
        2. Get regular_user's profile.
        3. Verify the profile data.
        """
        api_client.force_authenticate(user=another_user)
        
        response = api_client.get(f"/api/v1/accounts/profile/{regular_user.id}/")
        
        print(f"\nUser profile response:")
        print(json.dumps(response.json(), indent=4))
        
        assert response.status_code == 200
        
        json_resp = response.json()
        assert json_resp.get("success") == True
        
        profile_data = json_resp.get("response", {}).get("user", {})
        assert profile_data.get("id") == regular_user.id
        assert profile_data.get("email") == regular_user.email
        assert profile_data.get("issues_reported") == 1

    def test_get_nonexistent_user_profile(self, api_client, regular_user):
        """Test getting a non-existent user's profile."""
        api_client.force_authenticate(user=regular_user)
        
        response = api_client.get("/api/v1/accounts/profile/99999/")
        
        print(f"\nNonexistent user profile response:")
        print(json.dumps(response.json(), indent=4))
        
        assert response.status_code == 404


@pytest.mark.django_db
class TestUpdateProfile:
    """Test cases for update profile endpoint."""

    def test_update_profile(self, api_client, regular_user):
        """
        Test updating user profile.
        
        Scenario:
        1. Authenticate as user.
        2. Update profile with new info.
        3. Verify the updated info.
        """
        api_client.force_authenticate(user=regular_user)
        
        response = api_client.put("/api/v1/accounts/update-profile/", {
            "full_name": "Updated Name",
            "address": "456 New Street"
        }, format="json")
        
        print(f"\nUpdate profile response:")
        print(json.dumps(response.json(), indent=4))
        
        assert response.status_code == 200
        
        json_resp = response.json()
        assert json_resp.get("success") == True
        
        profile_data = json_resp.get("response", {})
        assert profile_data.get("full_name") == "Updated Name"
        assert profile_data.get("address") == "456 New Street"
        
        # Verify the changes persisted
        regular_user.refresh_from_db()
        assert regular_user.full_name == "Updated Name"
        assert regular_user.address == "456 New Street"

    def test_update_profile_partial(self, api_client, regular_user):
        """Test partial profile update."""
        api_client.force_authenticate(user=regular_user)
        
        original_name = regular_user.full_name
        
        response = api_client.put("/api/v1/accounts/update-profile/", {
            "phone_number": "+9876543210"
        }, format="json")
        
        print(f"\nPartial update profile response:")
        print(json.dumps(response.json(), indent=4))
        
        assert response.status_code == 200
        
        # Verify only phone_number changed
        regular_user.refresh_from_db()
        assert regular_user.phone_number == "+9876543210"
        assert regular_user.full_name == original_name

    def test_update_profile_without_auth(self, api_client):
        """Test that unauthenticated users cannot update profile."""
        response = api_client.put("/api/v1/accounts/update-profile/", {
            "full_name": "Hacker"
        }, format="json")
        
        print(f"\nUnauthenticated update response:")
        print(json.dumps(response.json(), indent=4))
        
        assert response.status_code == 401
