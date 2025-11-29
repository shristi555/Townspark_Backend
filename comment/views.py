from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Comment
from .serializers import (
    CommentSerializer,
    CommentCreateSerializer,
    CommentUpdateSerializer,
    CommentMineSerializer,
)


class IsOwnerOrAdmin(IsAuthenticated):
    """
    Custom permission to only allow owners of a comment or admins to edit/delete it.
    """
    def has_object_permission(self, request, view, obj):
        # Admins can do anything
        if request.user.is_admin or request.user.is_staff:
            return True
        # Owner can edit/delete their own comment
        return obj.user == request.user


class CommentCreateView(generics.CreateAPIView):
    """
    POST /comments/new/ - Create a new comment on an issue.
    
    Any authenticated user can create comments.
    """
    serializer_class = CommentCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CommentListByIssueView(generics.ListAPIView):
    """
    GET /comments/list/{issue_id}/ - List all comments for a specific issue.
    
    Any authenticated user can view comments on any issue.
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        issue_id = self.kwargs.get("issue_id")
        return Comment.objects.filter(issue_id=issue_id).order_by("-created_at")


class CommentUpdateView(generics.UpdateAPIView):
    """
    PUT/PATCH /comments/update/{id}/ - Update a comment.
    
    Only the user who created the comment can update it.
    """
    serializer_class = CommentUpdateSerializer
    permission_classes = [IsAuthenticated]
    queryset = Comment.objects.all()
    lookup_field = "id"
    
    def get_object(self):
        obj = super().get_object()
        # Only the owner can update their comment
        if obj.user != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You do not have permission to update this comment.")
        return obj


class CommentDeleteView(generics.DestroyAPIView):
    """
    DELETE /comments/delete/{id}/ - Delete a comment.
    
    Only the user who created the comment or an admin can delete it.
    """
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrAdmin]
    queryset = Comment.objects.all()
    lookup_field = "id"
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Check permission
        if not (request.user.is_admin or request.user.is_staff or instance.user == request.user):
            return Response(
                {"error": "You do not have permission to delete this comment."},
                status=status.HTTP_403_FORBIDDEN
            )
        self.perform_destroy(instance)
        return Response(
            {"message": "Comment deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )


# ============ Helper Endpoints ============

class CommentMineView(generics.ListAPIView):
    """
    GET /comments/mine/ - Retrieve all comments made by the authenticated user.
    """
    serializer_class = CommentMineSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Comment.objects.filter(user=self.request.user).order_by("-created_at")


class CommentsByIssueView(generics.ListAPIView):
    """
    GET /comments/issue/{issue_id}/ - List all comments for a specific issue.
    
    Same as CommentListByIssueView but with different URL path.
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        issue_id = self.kwargs.get("issue_id")
        return Comment.objects.filter(issue_id=issue_id).order_by("-created_at")


class CommentsByUserView(generics.ListAPIView):
    """
    GET /comments/user/{user_id}/ - List all comments made by a specific user.
    
    Only admins and staff can view comments by other users.
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user_id = self.kwargs.get("user_id")
        return Comment.objects.filter(user_id=user_id).order_by("-created_at")
    
    def list(self, request, *args, **kwargs):
        # Only staff or admin can view other users' comments
        if not (request.user.is_admin or request.user.is_staff):
            return Response(
                {"error": "Only admins and staff can view comments by other users."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().list(request, *args, **kwargs)

