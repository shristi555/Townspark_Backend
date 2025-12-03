import pytest
import json


@pytest.mark.django_db
def test_progress_addition_by_reporter():
    """Test that the reporter can add progress updates to their own issue."""
    pass


@pytest.mark.django_db
def test_progress_addition_by_admin_staff():
    """Test that admin/staff can add progress updates to any issue."""
    pass


@pytest.mark.django_db
def test_issue_progress_list_view():
    """Test listing all progress updates for a specific issue."""
    pass
