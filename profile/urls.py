from django.urls import path
from .views import (
    MyProfileView,
    UserProfileView,
    UpdateProfileView,
)

urlpatterns = [
    # Profile endpoints
    path("accounts/profile/mine/", MyProfileView.as_view(), name="my-profile"),
    path("accounts/profile/<int:user_id>/", UserProfileView.as_view(), name="user-profile"),
    path("accounts/update-profile/", UpdateProfileView.as_view(), name="update-profile"),
]
