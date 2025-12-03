from django.urls import path
from .views import (
    # Issue views
    IssueCreateView,
    IssueListView,
    IssueDetailView,
    IssueUpdateView,
    IssueDeleteView,
    UserReportedIssuesView,
    MyIssuesView,
    # Category views
    CategoryListView,
    CategoryCreateView,
)

urlpatterns = [
    # Issue endpoints
    path("issues/new/", IssueCreateView.as_view(), name="issue-create"),
    path("issues/list/", IssueListView.as_view(), name="issue-list"),
    path("issues/info/<int:issue_id>/", IssueDetailView.as_view(), name="issue-detail"),
    path("issues/user/<int:user_id>/", UserReportedIssuesView.as_view(), name="user-issues"),
    path("issues/my/", MyIssuesView.as_view(), name="my-issues"),
    path("issues/update/<int:issue_id>/", IssueUpdateView.as_view(), name="issue-update"),
    path("issues/delete/<int:issue_id>/", IssueDeleteView.as_view(), name="issue-delete"),
    
    # Category endpoints
    path("categories/list/", CategoryListView.as_view(), name="category-list"),
    path("categories/new/", CategoryCreateView.as_view(), name="category-create"),
]
