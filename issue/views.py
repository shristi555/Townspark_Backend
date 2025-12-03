from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404

from .models import Category, Issue, IssueImage
from .serializers import (
    CategorySerializer,
    CategoryCreateSerializer,
    IssueSerializer,
    IssueListSerializer,
    IssueCreateSerializer,
    IssueUpdateSerializer,
)
from .permissions import (
    IsAdmin,
    IsAdminOrStaff,
    IsReporterOrAdminOrStaff,
)


# ============================================================================
# Category Views
# ============================================================================

class CategoryListView(APIView):
    """
    GET /categories/list/ - List all categories
    
    No authentication required. Anyone can view the list of categories.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryCreateView(APIView):
    """
    POST /categories/new/ - Create a new category
    
    Requires authentication. Only admin users can create categories.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        serializer = CategoryCreateSerializer(data=request.data)
        if serializer.is_valid():
            category = serializer.save()
            return Response(
                CategorySerializer(category).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================================
# Issue Views
# ============================================================================

class IssueListView(APIView):
    """
    GET /issues/list/ - List all issues
    
    Requires authentication.
    Returns all issues with optional filtering by status, category, etc.
    
    Query params:
    - status: Filter by issue status (open, in_progress, resolved, closed)
    - category: Filter by category ID
    - search: Search in title and description
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        issues = Issue.objects.all().select_related(
            "category", "reported_by"
        ).prefetch_related("images")
        
        # Optional filtering by status
        status_filter = request.query_params.get("status")
        if status_filter:
            issues = issues.filter(status=status_filter)
        
        # Optional filtering by category
        category_id = request.query_params.get("category")
        if category_id:
            issues = issues.filter(category_id=category_id)
        
        # Optional search in title and description
        search = request.query_params.get("search")
        if search:
            from django.db.models import Q
            issues = issues.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        
        serializer = IssueListSerializer(issues, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class IssueCreateView(APIView):
    """
    POST /issues/new/ - Create a new issue
    
    Requires authentication. Any authenticated user can create an issue.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        serializer = IssueCreateSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IssueDetailView(APIView):
    """
    GET /issues/info/<int:issue_id>/ - Retrieve a specific issue by ID
    
    Requires authentication.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, issue_id):
        issue = get_object_or_404(
            Issue.objects.select_related("category", "reported_by").prefetch_related("images"),
            pk=issue_id
        )
        serializer = IssueSerializer(issue, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserReportedIssuesView(APIView):
    """
    GET /issues/user/<int:user_id>/ - List all issues reported by a specific user
    
    Requires authentication.
    - Regular users can only view their own issues
    - Admin/Staff can view any user's issues
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = request.user
        
        # Regular users can only view their own issues
        if not (user.is_admin or user.is_staff) and user.id != user_id:
            return Response(
                {"detail": "You can only view your own reported issues."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        issues = Issue.objects.filter(reported_by_id=user_id).select_related(
            "category", "reported_by"
        ).prefetch_related("images")
        
        serializer = IssueListSerializer(issues, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class MyIssuesView(APIView):
    """
    GET /issues/my/ - List all issues reported by the authenticated user
    
    Convenience endpoint for users to view their own reported issues.
    Requires authentication.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        issues = Issue.objects.filter(reported_by=request.user).select_related(
            "category", "reported_by"
        ).prefetch_related("images")
        
        serializer = IssueListSerializer(issues, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class IssueUpdateView(APIView):
    """
    PATCH /issues/update/<int:issue_id>/ - Update the status of a specific issue
    
    Requires authentication.
    Only admin/staff or the reporter of the issue can update the status.
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request, issue_id):
        issue = get_object_or_404(Issue, pk=issue_id)
        
        # Check if user is admin/staff or the reporter
        if not (request.user.is_admin or request.user.is_staff):
            if issue.reported_by != request.user:
                return Response(
                    {"detail": "Only the reporter, admin, or staff can update this issue."},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = IssueUpdateSerializer(
            issue, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IssueDeleteView(APIView):
    """
    DELETE /issues/delete/<int:issue_id>/ - Delete a specific issue
    
    Requires authentication.
    Only admin or the reporter of the issue can delete it.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, issue_id):
        issue = get_object_or_404(Issue, pk=issue_id)
        
        # Check if user is admin or the reporter
        if not request.user.is_admin:
            if issue.reported_by != request.user:
                return Response(
                    {"detail": "Only the reporter or admin can delete this issue."},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        issue.delete()
        return Response(
            {"detail": "Issue deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )
