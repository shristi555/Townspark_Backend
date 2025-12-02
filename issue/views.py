from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.shortcuts import get_object_or_404

from .models import Issue, IssueImage
from .serializers import (
    IssueSerializer,
    IssueCreateSerializer,
    IssueUpdateSerializer,
    IssueListSerializer,
    CategorySerializer,
)


class IsStaffOrAdmin(IsAuthenticated):
    """
    Custom permission to only allow staff or admin users.
    """
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.is_staff or request.user.is_admin


class IsOwnerOrStaffOrAdmin(IsAuthenticated):
    """
    Custom permission to allow:
    - Owner of the issue
    - Staff members
    - Admin users
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_admin:
            return True
        return obj.created_by == request.user


class IssueCreateView(APIView):
    """
    POST /issues/new - Create a new issue
    
    Requires authentication. Any authenticated user can create an issue.
    The creator is automatically set to the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = IssueCreateSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            issue = serializer.save()
            
            # Handle multiple image uploads
            images = request.FILES.getlist('images')
            for image in images:
                IssueImage.objects.create(issue=issue, image=image)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IssueListView(APIView):
    """
    GET /issues/list - List all issues
    
    Requires authentication.
    - Regular users see only their own issues
    - Staff and Admin users see all issues
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # Staff and admin can see all issues
        if user.is_staff or user.is_admin:
            issues = Issue.objects.all()
        else:
            # Regular users only see their own issues
            issues = Issue.objects.filter(created_by=user)
        
        # Optional filtering by status
        status_filter = request.query_params.get("status")
        if status_filter:
            issues = issues.filter(status=status_filter)
        
        # Optional filtering by category
        category_filter = request.query_params.get("category")
        if category_filter:
            issues = issues.filter(category=category_filter)
        
        serializer = IssueListSerializer(issues, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class IssueDetailView(APIView):
    """
    GET /issues/detail/{id}/ - Retrieve a specific issue
    
    Requires authentication.
    - Regular users can only view their own issues
    - Staff and Admin users can view any issue
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        issue = get_object_or_404(Issue, pk=pk)
        user = request.user
        
        # Check permission
        if not (user.is_staff or user.is_admin) and issue.created_by != user:
            return Response(
                {"error": "You do not have permission to view this issue."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = IssueSerializer(issue, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class IssueUpdateView(APIView):
    """
    PUT /issues/update/{id}/ - Update an issue
    
    Requires authentication.
    - Regular users can only update their own issues (title, description)
    - Staff and Admin users can update any issue including status
    - Only staff/admin can mark issues as resolved
    """
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        issue = get_object_or_404(Issue, pk=pk)
        user = request.user
        
        # Check permission
        if not (user.is_staff or user.is_admin) and issue.created_by != user:
            return Response(
                {"error": "You do not have permission to update this issue."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = IssueUpdateSerializer(
            issue, data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            
            # Handle multiple image uploads (add to existing images)
            images = request.FILES.getlist('images')
            for image in images:
                IssueImage.objects.create(issue=issue, image=image)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        """Partial update of an issue."""
        issue = get_object_or_404(Issue, pk=pk)
        user = request.user
        
        # Check permission
        if not (user.is_staff or user.is_admin) and issue.created_by != user:
            return Response(
                {"error": "You do not have permission to update this issue."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = IssueUpdateSerializer(
            issue, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            
            # Handle multiple image uploads (add to existing images)
            images = request.FILES.getlist('images')
            for image in images:
                IssueImage.objects.create(issue=issue, image=image)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IssueDeleteView(APIView):
    """
    DELETE /issues/delete/{id}/ - Delete an issue
    
    Requires authentication.
    - Regular users can only delete their own issues
    - Staff and Admin users can delete any issue
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        issue = get_object_or_404(Issue, pk=pk)
        user = request.user
        
        # Check permission
        if not (user.is_staff or user.is_admin) and issue.created_by != user:
            return Response(
                {"error": "You do not have permission to delete this issue."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        issue.delete()
        return Response(
            {"message": "Issue deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )


class CategoryListView(APIView):
    """
    GET /issues/categories/ - List all available issue categories
    
    No authentication required. Returns all category choices.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        categories = [
            {"value": value, "label": label}
            for value, label in Issue.CATEGORY_CHOICES
        ]
        return Response(categories, status=status.HTTP_200_OK)


class IssueByCategoryView(APIView):
    """
    GET /issues/category/{category}/ - List issues by category
    
    Requires authentication.
    - Regular users see only their own issues in the category
    - Staff and Admin users see all issues in the category
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, category):
        user = request.user
        
        # Validate category
        valid_categories = [choice[0] for choice in Issue.CATEGORY_CHOICES]
        if category not in valid_categories:
            return Response(
                {"error": f"Invalid category. Valid categories are: {', '.join(valid_categories)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Staff and admin can see all issues in category
        if user.is_staff or user.is_admin:
            issues = Issue.objects.filter(category=category)
        else:
            # Regular users only see their own issues in category
            issues = Issue.objects.filter(created_by=user, category=category)
        
        # Optional filtering by status
        status_filter = request.query_params.get("status")
        if status_filter:
            issues = issues.filter(status=status_filter)
        
        serializer = IssueListSerializer(issues, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
