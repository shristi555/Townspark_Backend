from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    CustomTokenObtainView,
    UserMeView,
    UserIssuesView,
    UserBookmarksView,
    UserUpvotedView,
    UserSettingsView,
    UserProfileView,
    ResolverRegisterView,
    ResolverDashboardView,
    ResolverAssignedView,
    ResolverPendingView,
    ResolverAcceptIssueView,
    ResolverCompleteIssueView,
    AdminDashboardView,
    AdminUsersView,
    AdminUserDetailView,
    AdminUserToggleStatusView,
    AdminResolversView,
    AdminResolversPendingView,
    AdminResolverVerifyView,
    AdminResolverRejectView,
    AdminResolverDeleteView,
)

urlpatterns = [
    # Auth endpoints
    path("auth/login/", CustomTokenObtainView.as_view(), name="login"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("auth/register/resolver/", ResolverRegisterView.as_view(), name="register-resolver"),
    
    # Include djoser URLs for register, password reset, etc.
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.jwt")),
    
    # User endpoints
    path("users/me/", UserMeView.as_view(), name="user-me"),
    path("users/me/issues/", UserIssuesView.as_view(), name="user-issues"),
    path("users/me/bookmarks/", UserBookmarksView.as_view(), name="user-bookmarks"),
    path("users/me/upvoted/", UserUpvotedView.as_view(), name="user-upvoted"),
    path("users/me/settings/", UserSettingsView.as_view(), name="user-settings"),
    path("users/<int:pk>/", UserProfileView.as_view(), name="user-profile"),
    
    # Resolver endpoints
    path("resolver/dashboard/", ResolverDashboardView.as_view(), name="resolver-dashboard"),
    path("resolver/assigned/", ResolverAssignedView.as_view(), name="resolver-assigned"),
    path("resolver/pending/", ResolverPendingView.as_view(), name="resolver-pending"),
    path("resolver/issues/<str:pk>/accept/", ResolverAcceptIssueView.as_view(), name="resolver-accept-issue"),
    path("resolver/issues/<str:pk>/complete/", ResolverCompleteIssueView.as_view(), name="resolver-complete-issue"),
    
    # Admin endpoints
    path("admin/dashboard/", AdminDashboardView.as_view(), name="admin-dashboard"),
    path("admin/users/", AdminUsersView.as_view(), name="admin-users"),
    path("admin/users/<int:pk>/", AdminUserDetailView.as_view(), name="admin-user-detail"),
    path("admin/users/<int:pk>/toggle-status/", AdminUserToggleStatusView.as_view(), name="admin-user-toggle-status"),
    path("admin/resolvers/", AdminResolversView.as_view(), name="admin-resolvers"),
    path("admin/resolvers/pending/", AdminResolversPendingView.as_view(), name="admin-resolvers-pending"),
    path("admin/resolvers/<int:pk>/verify/", AdminResolverVerifyView.as_view(), name="admin-resolver-verify"),
    path("admin/resolvers/<int:pk>/reject/", AdminResolverRejectView.as_view(), name="admin-resolver-reject"),
    path("admin/resolvers/<int:pk>/", AdminResolverDeleteView.as_view(), name="admin-resolver-delete"),
]
