from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from .views import IssueViewSet, CommentViewSet, CommentLikeView

# Main router
router = DefaultRouter()
router.register(r'issues', IssueViewSet, basename='issue')

# Nested router for comments under issues
issues_router = routers.NestedDefaultRouter(router, r'issues', lookup='issue')
issues_router.register(r'comments', CommentViewSet, basename='issue-comments')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(issues_router.urls)),
    path('comments/<uuid:pk>/like/', CommentLikeView.as_view(), name='comment-like'),
]
