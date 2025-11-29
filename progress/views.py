from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404

from .models import Progress, ProgressImage
from .serializers import (
    ProgressSerializer,
    ProgressCreateSerializer,
    ProgressUpdateSerializer,
    ProgressListSerializer,
)


class IsStaffOrAdmin(IsAuthenticated):
    """
    Custom permission to only allow staff or admin users.
    """
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.is_staff or request.user.is_admin


class ProgressCreateView(APIView):
    """
    POST /progress/new/ - Create a new progress update
    
    Requires authentication. Only staff/admin can create progress updates.
    Creates a progress entry and updates the related issue's status.
    """
    permission_classes = [IsStaffOrAdmin]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        serializer = ProgressCreateSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProgressListView(APIView):
    """
    GET /progress/list/ - List all progress updates
    
    Requires authentication.
    - Regular users see progress for their own issues
    - Staff and Admin users see all progress updates
    
    Optional query params:
    - issue_id: Filter by issue
    - status: Filter by status
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # Staff and admin can see all progress updates
        if user.is_staff or user.is_admin:
            progress_updates = Progress.objects.all()
        else:
            # Regular users only see progress for their own issues
            progress_updates = Progress.objects.filter(issue__created_by=user)
        
        # Optional filtering by issue_id
        issue_id = request.query_params.get("issue_id")
        if issue_id:
            progress_updates = progress_updates.filter(issue_id=issue_id)
        
        # Optional filtering by status
        status_filter = request.query_params.get("status")
        if status_filter:
            progress_updates = progress_updates.filter(status=status_filter)
        
        # Optimize query
        progress_updates = progress_updates.select_related("issue", "updated_by").prefetch_related("images")
        
        serializer = ProgressListSerializer(progress_updates, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProgressDetailView(APIView):
    """
    GET /progress/detail/{id}/ - Retrieve a specific progress update
    
    Requires authentication.
    - Regular users can only view progress for their own issues
    - Staff and Admin users can view any progress update
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        progress = get_object_or_404(
            Progress.objects.select_related("issue", "updated_by").prefetch_related("images"),
            pk=pk
        )
        user = request.user
        
        # Check permission
        if not (user.is_staff or user.is_admin) and progress.issue.created_by != user:
            return Response(
                {"error": "You do not have permission to view this progress update."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ProgressSerializer(progress, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProgressUpdateView(APIView):
    """
    PUT /progress/update/{id}/ - Update a progress update
    
    Requires authentication. Only staff/admin can update progress.
    """
    permission_classes = [IsStaffOrAdmin]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def put(self, request, pk):
        progress = get_object_or_404(Progress, pk=pk)
        
        serializer = ProgressUpdateSerializer(
            progress, data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        """Partial update of a progress update."""
        progress = get_object_or_404(Progress, pk=pk)
        
        serializer = ProgressUpdateSerializer(
            progress, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProgressDeleteView(APIView):
    """
    DELETE /progress/delete/{id}/ - Delete a progress update
    
    Requires authentication. Only staff/admin can delete progress.
    """
    permission_classes = [IsStaffOrAdmin]

    def delete(self, request, pk):
        progress = get_object_or_404(Progress, pk=pk)
        
        # Delete associated images first (they will be deleted via CASCADE, but good practice)
        progress.delete()
        
        return Response(
            {"message": "Progress update deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )


class ProgressByIssueView(APIView):
    """
    GET /progress/issue/{issue_id}/ - List all progress updates for a specific issue
    
    Requires authentication.
    - Regular users can only view progress for their own issues
    - Staff and Admin users can view progress for any issue
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, issue_id):
        from issue.models import Issue
        
        issue = get_object_or_404(Issue, pk=issue_id)
        user = request.user
        
        # Check permission
        if not (user.is_staff or user.is_admin) and issue.created_by != user:
            return Response(
                {"error": "You do not have permission to view progress for this issue."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        progress_updates = Progress.objects.filter(issue=issue).select_related(
            "issue", "updated_by"
        ).prefetch_related("images")
        
        serializer = ProgressListSerializer(progress_updates, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
