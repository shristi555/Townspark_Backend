from django.urls import path
from .views import (
    ProgressCreateView,
    ProgressListView,
    ProgressDetailView,
    ProgressUpdateView,
    ProgressDeleteView,
    ProgressByIssueView,
)

urlpatterns = [
    # Progress CRUD endpoints
    path("progress/new/", ProgressCreateView.as_view(), name="progress-create"),
    path("progress/list/", ProgressListView.as_view(), name="progress-list"),
    path("progress/detail/<int:pk>/", ProgressDetailView.as_view(), name="progress-detail"),
    path("progress/update/<int:pk>/", ProgressUpdateView.as_view(), name="progress-update"),
    path("progress/delete/<int:pk>/", ProgressDeleteView.as_view(), name="progress-delete"),
    
    # Helper endpoint
    path("progress/issue/<int:issue_id>/", ProgressByIssueView.as_view(), name="progress-by-issue"),
]
