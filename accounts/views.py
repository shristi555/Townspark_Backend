from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView

from core.utils.response_models import ErrorResponse

User = get_user_model()


class CustomTokenObtainView(TokenObtainPairView):
    """
    Custom view to handle user login with additional checks:
    - Verify if the email exists.
    - Check if the account is active.
    - Validate the password.

    it is intended to give a detailed error response for each failure case. overriding the default behavior of djoser's TokenCreateView.
    """

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return ErrorResponse(
                error_message="Email does not exist",
                error_details={"email": "No account found with the provided email"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if not user.is_active:
            return ErrorResponse(
                error_message="Account is inactive",
                error_details={
                    "email": "The account associated with this email is inactive. Please contact support."
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, email=email, password=password)
        if user is None:
            return ErrorResponse(
                error_message="Invalid password",
                error_details={
                    "password": "The provided password is incorrect for given email."
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        tokensResponse = super().post(request, *args, **kwargs)

        #         send user info along with tokens
        if tokensResponse.status_code == status.HTTP_200_OK:
            tokensData = tokensResponse.data
            userData = user.get_user_info()
            combinedData = {"tokens": tokensData, "user": userData}
            return Response(combinedData, status=status.HTTP_200_OK)

        else:
            return ErrorResponse(
                error_message="Authentication failed",
                error_details={
                    "detail": "Unable to authenticate with provided credentials."
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        return None
