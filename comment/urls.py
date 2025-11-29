from django.urls import path
from .views import (
    CommentCreateView,
    CommentListByIssueView,
    CommentUpdateView,
    CommentDeleteView,
    CommentMineView,
    CommentsByIssueView,
    CommentsByUserView,
)

urlpatterns = [
    # Main CRUD endpoints
    path("new/", CommentCreateView.as_view(), name="comment-create"),
    path("list/<int:issue_id>/", CommentListByIssueView.as_view(), name="comment-list"),
    path("update/<int:id>/", CommentUpdateView.as_view(), name="comment-update"),
    path("delete/<int:id>/", CommentDeleteView.as_view(), name="comment-delete"),
    
    # Helper endpoints
    path("mine/", CommentMineView.as_view(), name="comment-mine"),
    path("issue/<int:issue_id>/", CommentsByIssueView.as_view(), name="comments-by-issue"),
    path("user/<int:user_id>/", CommentsByUserView.as_view(), name="comments-by-user"),
]
