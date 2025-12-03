from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404

from .serializers import (
    UserSerializer,
    ProfileSerializer,
    ProfileUpdateSerializer,
)

User = get_user_model()


class MyProfileView(APIView):
    """
    GET /accounts/profile/mine/ - Get authenticated user's profile
    
    Returns the user's profile information including:
    - User basic info (id, email, full_name, etc.)
    - Number of issues reported
    - Number of progress updates made
    - List of issues reported by the user
    
    Requires authentication.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = ProfileSerializer(user, context={"request": request})
        return Response({"user": serializer.data}, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    """
    GET /accounts/profile/<user_id>/ - Get another user's profile
    
    Returns a user's public profile information including:
    - User basic info (id, email, full_name, etc.)
    - Number of issues reported
    - Number of progress updates made
    - List of issues reported by the user
    
    Requires authentication.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        serializer = ProfileSerializer(user, context={"request": request})
        return Response({"user": serializer.data}, status=status.HTTP_200_OK)


class UpdateProfileView(APIView):
    """
    PUT /accounts/update-profile/ - Update authenticated user's profile
    
    Allows updating:
    - full_name
    - phone_number
    - address
    - profile_image
    
    Requires authentication.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def put(self, request):
        user = request.user
        serializer = ProfileUpdateSerializer(
            user,
            data=request.data,
            partial=True,
            context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
