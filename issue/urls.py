from django.urls import path
from .views import (
    IssueCreateView,
    IssueListView,
    IssueDetailView,
    IssueUpdateView,
    IssueDeleteView,
)

urlpatterns = [
    # Issue CRUD endpoints
    path("issues/new/", IssueCreateView.as_view(), name="issue-create"),
    path("issues/list/", IssueListView.as_view(), name="issue-list"),
    path("issues/detail/<int:pk>/", IssueDetailView.as_view(), name="issue-detail"),
    path("issues/update/<int:pk>/", IssueUpdateView.as_view(), name="issue-update"),
    path("issues/delete/<int:pk>/", IssueDeleteView.as_view(), name="issue-delete"),
]
