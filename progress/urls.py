from django.urls import path
from .views import (
    ProgressCreateView,
    IssueProgressListView,
)

urlpatterns = [
    # Progress endpoints
    path("progress/new/", ProgressCreateView.as_view(), name="progress-create"),
    path("progress/issue/<int:issue_id>/", IssueProgressListView.as_view(), name="issue-progress-list"),
]
