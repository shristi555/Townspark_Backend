from django.contrib.auth import authenticate, get_user_model
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .serializers import (
    UserCreateSerializer,
    UserSerializer,
    UserUpdateSerializer,
    LoginSerializer,
)

User = get_user_model()


class SignupView(APIView):
    """
    POST /auth/signup/ - User Registration
    
    Creates a new user account.
    Returns the created user object without sensitive information.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            response_serializer = UserSerializer(user, context={"request": request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    POST /auth/login/ - User Login (Token Creation)
    
    Authenticates user and returns JWT tokens along with user object.
    Provides detailed error responses for each failure case.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        # Check if email exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "Email does not exist", "details": {"email": "No account found with the provided email"}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if account is active
        if not user.is_active:
            return Response(
                {"error": "Account is inactive", "details": {"email": "The account associated with this email is inactive. Please contact support."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Authenticate user
        user = authenticate(request, email=email, password=password)
        if user is None:
            return Response(
                {"error": "Invalid password", "details": {"password": "The provided password is incorrect for given email."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        tokens = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

        # Return tokens and user info
        user_serializer = UserSerializer(user, context={"request": request})
        return Response(
            {"tokens": tokens, "user": user_serializer.data},
            status=status.HTTP_200_OK,
        )


class CustomTokenRefreshView(TokenRefreshView):
    """
    POST /auth/jwt/refresh/ - Token Refresh
    
    Refreshes access token using refresh token.
    Returns new access and refresh tokens.
    """
    pass


class CustomTokenVerifyView(TokenVerifyView):
    """
    POST /auth/jwt/verify/ - Token Verification
    
    Verifies if a token is valid.
    """
    pass


class UserMeView(APIView):
    """
    GET /auth/users/me/ - Get Current User Profile
    PUT/PATCH /auth/users/me/ - Update Current User Profile
    
    Requires authentication.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return the current authenticated user's profile."""
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        """Update the current authenticated user's profile (full update)."""
        serializer = UserUpdateSerializer(
            request.user, data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        """Update the current authenticated user's profile (partial update)."""
        serializer = UserUpdateSerializer(
            request.user, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
