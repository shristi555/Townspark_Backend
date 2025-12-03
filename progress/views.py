from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404

from .models import Progress, ProgressImage
from .serializers import ProgressSerializer, ProgressCreateSerializer
from issue.models import Issue


class ProgressCreateView(APIView):
    """
    POST /progress/new/ - Create a new progress update
    
    Requires authentication.
    Only the reporter, admin, or staff members can create progress updates.
    Creates a progress entry and updates the related issue's updated_at timestamp.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        serializer = ProgressCreateSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IssueProgressListView(APIView):
    """
    GET /progress/issue/<int:issue_id>/ - List all progress updates for a specific issue
    
    Requires authentication.
    Returns all progress updates for a specific issue ordered by creation time (newest first).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, issue_id):
        # Verify the issue exists
        issue = get_object_or_404(Issue, pk=issue_id)
        
        # Get all progress updates for this issue
        progress_updates = Progress.objects.filter(issue=issue).select_related(
            "updated_by"
        ).prefetch_related("images")
        
        serializer = ProgressSerializer(progress_updates, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
