from django.urls import path
from .views import (
    SignupView,
    LoginView,
    CustomTokenRefreshView,
    CustomTokenVerifyView,
    UserMeView,
)

urlpatterns = [
    # Authentication endpoints
    path("auth/register/", SignupView.as_view(), name="signup"),
    path("auth/login/", LoginView.as_view(), name="login"),
    
    # JWT token management
    path("auth/token/refresh/", CustomTokenRefreshView.as_view(), name="token-refresh"),
    path("auth/token/verify/", CustomTokenVerifyView.as_view(), name="token-verify"),
    
    # User profile management
    path("auth/profile/", UserMeView.as_view(), name="user-me"),
]
