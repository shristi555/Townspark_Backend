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
    path("auth/signup/", SignupView.as_view(), name="signup"),
    path("auth/login/", LoginView.as_view(), name="login"),
    
    # JWT token management
    path("auth/jwt/refresh/", CustomTokenRefreshView.as_view(), name="token-refresh"),
    path("auth/jwt/verify/", CustomTokenVerifyView.as_view(), name="token-verify"),
    
    # User profile management
    path("auth/users/me/", UserMeView.as_view(), name="user-me"),
]
