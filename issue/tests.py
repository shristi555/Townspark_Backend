import pytest
import json
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from issue.models import Category, Issue, IssueImage

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
def admin_user(db, create_user):
    """Create an admin user."""
    return create_user(
        email="admin@test.com",
        password="admin@Test123",
        full_name="Admin User",
        is_admin=True
    )


@pytest.fixture
def staff_user(db, create_user):
    """Create a staff user."""
    return create_user(
        email="staff@test.com",
        password="staff@Test123",
        full_name="Staff User",
        is_staff=True
    )


@pytest.fixture
def regular_user(db, create_user):
    """Create a regular user."""
    return create_user(
        email="user@test.com",
        password="user@Test123",
        full_name="Regular User"
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


def authenticate_user(api_client, email, password):
    """Helper function to authenticate a user and set the token."""
    response = api_client.post("/api/v1/auth/login/", {
        "email": email,
        "password": password
    })
    json_response = response.json()
    if json_response.get("success"):
        tokens = json_response.get("response", {}).get("tokens", {})
        access_token = tokens.get("access")
        if access_token:
            api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
            return True
    return False


@pytest.mark.django_db
class TestIssueCreation:
    """Test cases for issue creation."""

    def test_new_issue_creation(self, api_client, regular_user, category):
        """
        Test creating a new issue.
        
        Scenario:
        1. Create a new issue with title, description, category, location.
        2. Verify that the issue is created successfully.
        3. Verify that the issue is associated with the correct user.
        4. Verify that the issue has the correct title, description, category, location.
        5. Verify that the issue's status is set to 'open' by default.
        """
        # Authenticate user
        api_client.force_authenticate(user=regular_user)
        
        # Create a new issue
        response = api_client.post("/api/v1/issues/new/", {
            "title": "Test Issue",
            "description": "This is a test issue description.",
            "category": category.id,
            "location": "Test Location"
        }, format="json")
        
        print(f"\nIssue creation response:")
        print(json.dumps(response.json(), indent=4))
        
        assert response.status_code == 201, f"Issue creation failed with status code {response.status_code}"
        
        json_resp = response.json()
        assert json_resp.get("success") == True
        
        issue_data = json_resp.get("response", {})
        assert issue_data.get("title") == "Test Issue"
        assert issue_data.get("description") == "This is a test issue description."
        assert issue_data.get("location") == "Test Location"
        assert issue_data.get("status") == "open"
        assert issue_data.get("category", {}).get("id") == category.id
        assert issue_data.get("reported_by", {}).get("id") == regular_user.id

    def test_issue_creation_without_auth(self, api_client, category):
        """Test that unauthenticated users cannot create issues."""
        response = api_client.post("/api/v1/issues/new/", {
            "title": "Test Issue",
            "description": "This is a test issue description.",
            "category": category.id,
            "location": "Test Location"
        }, format="json")
        
        print(f"\nUnauthenticated issue creation response:")
        print(json.dumps(response.json(), indent=4))
        
        assert response.status_code == 401


@pytest.mark.django_db
class TestIssueListView:
    """Test cases for listing issues."""

    def test_issue_list_view(self, api_client, regular_user, issue):
        """
        Test listing all issues.
        
        Scenario:
        1. Authenticate as a user.
        2. List all issues.
        3. Verify that the issues are returned.
        """
        api_client.force_authenticate(user=regular_user)
        
        response = api_client.get("/api/v1/issues/list/")
        
        print(f"\nIssue list response:")
        print(json.dumps(response.json(), indent=4))
        
        assert response.status_code == 200
        
        json_resp = response.json()
        assert json_resp.get("success") == True
        
        issues = json_resp.get("response", [])
        assert len(issues) >= 1

    def test_issue_list_filter_by_status(self, api_client, regular_user, issue):
        """Test filtering issues by status."""
        api_client.force_authenticate(user=regular_user)
        
        response = api_client.get("/api/v1/issues/list/?status=open")
        
        print(f"\nFiltered issue list response:")
        print(json.dumps(response.json(), indent=4))
        
        assert response.status_code == 200


@pytest.mark.django_db
class TestIssueDetailView:
    """Test cases for retrieving a specific issue."""

    def test_specific_issue_retrieval(self, api_client, regular_user, issue):
        """
        Test retrieving a specific issue by ID.
        
        Scenario:
        1. Authenticate as a user.
        2. Retrieve a specific issue by ID.
        3. Verify that the issue details are correct.
        """
        api_client.force_authenticate(user=regular_user)
        
        response = api_client.get(f"/api/v1/issues/info/{issue.id}/")
        
        print(f"\nIssue detail response:")
        print(json.dumps(response.json(), indent=4))
        
        assert response.status_code == 200
        
        json_resp = response.json()
        assert json_resp.get("success") == True
        
        issue_data = json_resp.get("response", {})
        assert issue_data.get("id") == issue.id
        assert issue_data.get("title") == issue.title

    def test_issue_not_found(self, api_client, regular_user):
        """Test that a 404 is returned for non-existent issue."""
        api_client.force_authenticate(user=regular_user)
        
        response = api_client.get("/api/v1/issues/info/99999/")
        
        print(f"\nIssue not found response:")
        print(json.dumps(response.json(), indent=4))
        
        assert response.status_code == 404


@pytest.mark.django_db
class TestUserReportedIssues:
    """Test cases for user reported issues."""

    def test_user_reported_issues(self, api_client, regular_user, issue):
        """
        Test listing all issues reported by the authenticated user.
        
        Scenario:
        1. Authenticate as a user.
        2. List all issues reported by the user.
        3. Verify that only the user's issues are returned.
        """
        api_client.force_authenticate(user=regular_user)
        
        response = api_client.get(f"/api/v1/issues/user/{regular_user.id}/")
        
        print(f"\nUser reported issues response:")
        print(json.dumps(response.json(), indent=4))
        
        assert response.status_code == 200
        
        json_resp = response.json()
        assert json_resp.get("success") == True
        
        issues = json_resp.get("response", [])
        for issue_data in issues:
            assert issue_data.get("reported_by", {}).get("id") == regular_user.id

    def test_cannot_view_other_users_issues(self, api_client, regular_user, admin_user, issue):
        """Test that regular users cannot view other users' issues via user endpoint."""
        api_client.force_authenticate(user=regular_user)
        
        response = api_client.get(f"/api/v1/issues/user/{admin_user.id}/")
        
        print(f"\nOther user's issues response:")
        print(json.dumps(response.json(), indent=4))
        
        assert response.status_code == 403


@pytest.mark.django_db
class TestIssueStatusUpdate:
    """Test cases for updating issue status."""

    def test_issue_status_update_by_reporter(self, api_client, regular_user, issue):
        """
        Test updating the status of an issue by the reporter.
        
        Scenario:
        1. Authenticate as the reporter.
        2. Update the issue status.
        3. Verify that the status is updated.
        """
        api_client.force_authenticate(user=regular_user)
        
        response = api_client.patch(
            f"/api/v1/issues/update/{issue.id}/",
            {"status": "in_progress"},
            format="json"
        )
        
        print(f"\nIssue status update by reporter response:")
        print(json.dumps(response.json(), indent=4))
        
        assert response.status_code == 200
        
        json_resp = response.json()
        assert json_resp.get("success") == True
        assert json_resp.get("response", {}).get("status") == "in_progress"

    def test_issue_status_update_by_admin(self, api_client, admin_user, issue):
        """
        Test updating the status of an issue by admin.
        
        Scenario:
        1. Authenticate as admin.
        2. Update the issue status.
        3. Verify that the status is updated.
        """
        api_client.force_authenticate(user=admin_user)
        
        response = api_client.patch(
            f"/api/v1/issues/update/{issue.id}/",
            {"status": "resolved"},
            format="json"
        )
        
        print(f"\nIssue status update by admin response:")
        print(json.dumps(response.json(), indent=4))
        
        assert response.status_code == 200
        
        json_resp = response.json()
        assert json_resp.get("success") == True
        assert json_resp.get("response", {}).get("status") == "resolved"

    def test_issue_status_update_by_staff(self, api_client, staff_user, issue):
        """Test updating the status of an issue by staff."""
        api_client.force_authenticate(user=staff_user)
        
        response = api_client.patch(
            f"/api/v1/issues/update/{issue.id}/",
            {"status": "closed"},
            format="json"
        )
        
        print(f"\nIssue status update by staff response:")
        print(json.dumps(response.json(), indent=4))
        
        assert response.status_code == 200

    def test_issue_status_update_by_other_user(self, api_client, create_user, issue):
        """Test that other users cannot update issue status."""
        other_user = create_user(
            email="other@test.com",
            password="other@Test123",
            full_name="Other User"
        )
        api_client.force_authenticate(user=other_user)
        
        response = api_client.patch(
            f"/api/v1/issues/update/{issue.id}/",
            {"status": "resolved"},
            format="json"
        )
        
        print(f"\nIssue status update by other user response:")
        print(json.dumps(response.json(), indent=4))
        
        assert response.status_code == 403


@pytest.mark.django_db
class TestCategoryViews:
    """Test cases for category views."""

    def test_category_list_view(self, api_client, category):
        """
        Test listing all categories.
        
        Scenario:
        1. List all categories (no auth required).
        2. Verify that categories are returned.
        """
        response = api_client.get("/api/v1/categories/list/")
        
        print(f"\nCategory list response:")
        print(json.dumps(response.json(), indent=4))
        
        assert response.status_code == 200
        
        json_resp = response.json()
        assert json_resp.get("success") == True
        
        categories = json_resp.get("response", [])
        assert len(categories) >= 1

    def test_category_creation_by_admin(self, api_client, admin_user):
        """
        Test creating a new category by admin.
        
        Scenario:
        1. Authenticate as admin.
        2. Create a new category.
        3. Verify that the category is created.
        """
        api_client.force_authenticate(user=admin_user)
        
        response = api_client.post("/api/v1/categories/new/", {
            "name": "Streetlight Outages",
            "description": "Issues related to streetlight outages."
        }, format="json")
        
        print(f"\nCategory creation by admin response:")
        print(json.dumps(response.json(), indent=4))
        
        assert response.status_code == 201
        
        json_resp = response.json()
        assert json_resp.get("success") == True
        assert json_resp.get("response", {}).get("name") == "Streetlight Outages"

    def test_category_creation_by_non_admin(self, api_client, regular_user):
        """
        Test that non-admin users cannot create categories.
        
        Scenario:
        1. Authenticate as a regular user.
        2. Attempt to create a new category.
        3. Verify that the request is denied (403).
        """
        api_client.force_authenticate(user=regular_user)
        
        response = api_client.post("/api/v1/categories/new/", {
            "name": "Graffiti",
            "description": "Issues related to graffiti."
        }, format="json")
        
        print(f"\nCategory creation by non-admin response:")
        print(json.dumps(response.json(), indent=4))
        
        assert response.status_code == 403

    def test_category_creation_by_staff(self, api_client, staff_user):
        """Test that staff users cannot create categories (only admin can)."""
        api_client.force_authenticate(user=staff_user)
        
        response = api_client.post("/api/v1/categories/new/", {
            "name": "Vandalism",
            "description": "Issues related to vandalism."
        }, format="json")
        
        print(f"\nCategory creation by staff response:")
        print(json.dumps(response.json(), indent=4))
        
        assert response.status_code == 403


@pytest.mark.django_db
class TestProgressViews:
    """Test cases for progress views."""

    def test_progress_addition_by_reporter(self, api_client, regular_user, issue):
        """
        Test adding progress updates to an issue by the reporter.
        
        Scenario:
        1. Authenticate as the reporter.
        2. Add a progress update to the issue.
        3. Verify that the progress is added.
        """
        api_client.force_authenticate(user=regular_user)
        
        response = api_client.post("/api/v1/progress/new/", {
            "issue": issue.id,
            "description": "Started working on the pothole."
        }, format="json")
        
        print(f"\nProgress addition by reporter response:")
        print(json.dumps(response.json(), indent=4))
        
        assert response.status_code == 201
        
        json_resp = response.json()
        assert json_resp.get("success") == True

    def test_progress_addition_by_admin_staff(self, api_client, admin_user, issue):
        """
        Test adding progress updates to an issue by admin/staff.
        
        Scenario:
        1. Authenticate as admin.
        2. Add a progress update to any issue.
        3. Verify that the progress is added.
        """
        api_client.force_authenticate(user=admin_user)
        
        response = api_client.post("/api/v1/progress/new/", {
            "issue": issue.id,
            "description": "Admin is reviewing this issue."
        }, format="json")
        
        print(f"\nProgress addition by admin response:")
        print(json.dumps(response.json(), indent=4))
        
        assert response.status_code == 201

    def test_progress_addition_by_other_user(self, api_client, create_user, issue):
        """Test that other users cannot add progress to an issue."""
        other_user = create_user(
            email="other2@test.com",
            password="other@Test123",
            full_name="Other User 2"
        )
        api_client.force_authenticate(user=other_user)
        
        response = api_client.post("/api/v1/progress/new/", {
            "issue": issue.id,
            "description": "Unauthorized progress update."
        }, format="json")
        
        print(f"\nProgress addition by other user response:")
        print(json.dumps(response.json(), indent=4))
        
        assert response.status_code == 400  # Serializer validation error

    def test_issue_progress_list_view(self, api_client, regular_user, issue):
        """
        Test listing all progress updates for a specific issue.
        
        Scenario:
        1. Add some progress updates.
        2. List all progress updates for the issue.
        3. Verify that all progress updates are returned.
        """
        from progress.models import Progress
        
        # Create some progress updates
        Progress.objects.create(
            issue=issue,
            description="Progress update 1",
            updated_by=regular_user
        )
        Progress.objects.create(
            issue=issue,
            description="Progress update 2",
            updated_by=regular_user
        )
        
        api_client.force_authenticate(user=regular_user)
        
        response = api_client.get(f"/api/v1/progress/issue/{issue.id}/")
        
        print(f"\nIssue progress list response:")
        print(json.dumps(response.json(), indent=4))
        
        assert response.status_code == 200
        
        json_resp = response.json()
        assert json_resp.get("success") == True
        
        progress_list = json_resp.get("response", [])
        assert len(progress_list) >= 2