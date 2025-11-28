from rest_framework import viewsets, views, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q

from .models import (
    Issue, IssueImage, IssueTimeline, OfficialResponse,
    Comment, CommentLike, Upvote, Bookmark
)
from .serializers import (
    IssueListSerializer, IssueDetailSerializer, IssueCreateSerializer,
    IssueUpdateSerializer, IssueStatusUpdateSerializer, IssueAssignSerializer,
    CommentSerializer, CommentCreateSerializer, OfficialResponseCreateSerializer
)
from .permissions import IsOwnerOrReadOnly, IsResolverOrAdmin
from .filters import IssueFilter
from core.utils.response_models import SuccessResponse, ErrorResponse, PaginatedResponse


class IssueViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Issue CRUD operations and related actions.
    """
    queryset = Issue.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'address', 'area']
    ordering_fields = ['created_at', 'upvote_count', 'comment_count']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return IssueListSerializer
        elif self.action == 'create':
            return IssueCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return IssueUpdateSerializer
        return IssueDetailSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        elif self.action == 'create':
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = Issue.objects.select_related(
            'reporter', 'category', 'department', 'assigned_resolver'
        ).prefetch_related('images', 'timeline', 'upvotes', 'bookmarks')
        
        # Apply filters
        params = self.request.query_params
        
        if params.get('status'):
            statuses = params.get('status').split(',')
            queryset = queryset.filter(status__in=statuses)
        
        if params.get('category'):
            categories = params.get('category').split(',')
            queryset = queryset.filter(category_id__in=categories)
        
        if params.get('urgency'):
            urgencies = params.get('urgency').split(',')
            queryset = queryset.filter(urgency__in=urgencies)
        
        if params.get('area'):
            queryset = queryset.filter(area__icontains=params.get('area'))
        
        # Sort options
        sort = params.get('sort', 'newest')
        if sort == 'oldest':
            queryset = queryset.order_by('created_at')
        elif sort == 'most_upvotes':
            queryset = queryset.order_by('-upvote_count')
        elif sort == 'most_comments':
            queryset = queryset.order_by('-comment_count')
        else:  # newest
            queryset = queryset.order_by('-created_at')
        
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return SuccessResponse(data=serializer.data, message="Issues retrieved successfully")

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return SuccessResponse(data=serializer.data, message="Issue retrieved successfully")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(reporter=request.user)
            detail_serializer = IssueDetailSerializer(
                serializer.instance, 
                context={'request': request}
            )
            return SuccessResponse(
                data=detail_serializer.data,
                message="Issue reported successfully",
                status_code=status.HTTP_201_CREATED
            )
        return ErrorResponse(
            error_message="Validation failed",
            error_details=serializer.errors,
            error_code="VALIDATION_ERROR"
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            detail_serializer = IssueDetailSerializer(
                instance, 
                context={'request': request}
            )
            return SuccessResponse(
                data=detail_serializer.data,
                message="Issue updated successfully"
            )
        return ErrorResponse(
            error_message="Validation failed",
            error_details=serializer.errors,
            error_code="VALIDATION_ERROR"
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return SuccessResponse(message="Issue deleted successfully")

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def upvote(self, request, pk=None):
        """Toggle upvote on an issue."""
        issue = self.get_object()
        upvote, created = Upvote.objects.get_or_create(
            user=request.user,
            issue=issue
        )
        
        if not created:
            upvote.delete()
            issue.update_upvote_count()
            return SuccessResponse(
                data={'upvoted': False, 'upvotes': issue.upvote_count},
                message="Upvote removed"
            )
        
        issue.update_upvote_count()
        return SuccessResponse(
            data={'upvoted': True, 'upvotes': issue.upvote_count},
            message="Issue upvoted"
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def bookmark(self, request, pk=None):
        """Toggle bookmark on an issue."""
        issue = self.get_object()
        bookmark, created = Bookmark.objects.get_or_create(
            user=request.user,
            issue=issue
        )
        
        if not created:
            bookmark.delete()
            return SuccessResponse(
                data={'bookmarked': False},
                message="Bookmark removed"
            )
        
        return SuccessResponse(
            data={'bookmarked': True},
            message="Issue bookmarked"
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def share(self, request, pk=None):
        """Track share action."""
        issue = self.get_object()
        issue.share_count += 1
        issue.save(update_fields=['share_count'])
        return SuccessResponse(
            data={'shares': issue.share_count},
            message="Share tracked"
        )

    @action(detail=True, methods=['patch'], url_path='status', permission_classes=[IsAuthenticated, IsResolverOrAdmin])
    def update_status(self, request, pk=None):
        """Update issue status (resolver/admin only)."""
        issue = self.get_object()
        serializer = IssueStatusUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            new_status = serializer.validated_data['status']
            note = serializer.validated_data.get('note', '')
            
            issue.status = new_status
            if new_status == Issue.Status.RESOLVED:
                issue.resolved_at = timezone.now()
            issue.save()
            
            # Create timeline entry
            IssueTimeline.objects.create(
                issue=issue,
                status=new_status,
                note=note,
                updated_by=request.user
            )
            
            detail_serializer = IssueDetailSerializer(issue, context={'request': request})
            return SuccessResponse(
                data=detail_serializer.data,
                message="Status updated successfully"
            )
        
        return ErrorResponse(
            error_message="Validation failed",
            error_details=serializer.errors,
            error_code="VALIDATION_ERROR"
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def assign(self, request, pk=None):
        """Assign issue to resolver (admin only)."""
        issue = self.get_object()
        serializer = IssueAssignSerializer(data=request.data)
        
        if serializer.is_valid():
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            try:
                resolver = User.objects.get(id=serializer.validated_data['resolver_id'])
                issue.assigned_resolver = resolver
                issue.save()
                
                # Create timeline entry
                IssueTimeline.objects.create(
                    issue=issue,
                    status=issue.status,
                    note=f"Assigned to {resolver.full_name}",
                    updated_by=request.user
                )
                
                return SuccessResponse(
                    data={'assigned_to': resolver.full_name},
                    message="Issue assigned successfully"
                )
            except User.DoesNotExist:
                return ErrorResponse(
                    error_message="Resolver not found",
                    error_code="NOT_FOUND",
                    status_code=status.HTTP_404_NOT_FOUND
                )
        
        return ErrorResponse(
            error_message="Validation failed",
            error_details=serializer.errors,
            error_code="VALIDATION_ERROR"
        )

    @action(detail=True, methods=['post'], url_path='official-response', permission_classes=[IsAuthenticated, IsResolverOrAdmin])
    def official_response(self, request, pk=None):
        """Add official response (resolver/admin only)."""
        issue = self.get_object()
        
        # Check if official response already exists
        if hasattr(issue, 'official_response'):
            return ErrorResponse(
                error_message="Official response already exists",
                error_code="DUPLICATE_ENTRY",
                status_code=status.HTTP_409_CONFLICT
            )
        
        serializer = OfficialResponseCreateSerializer(data=request.data)
        if serializer.is_valid():
            OfficialResponse.objects.create(
                issue=issue,
                department=issue.department,
                message=serializer.validated_data['message'],
                responder=request.user
            )
            
            detail_serializer = IssueDetailSerializer(issue, context={'request': request})
            return SuccessResponse(
                data=detail_serializer.data,
                message="Official response added successfully"
            )
        
        return ErrorResponse(
            error_message="Validation failed",
            error_details=serializer.errors,
            error_code="VALIDATION_ERROR"
        )


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Comment operations.
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        issue_id = self.kwargs.get('issue_pk')
        return Comment.objects.filter(
            issue_id=issue_id,
            parent__isnull=True  # Only top-level comments
        ).select_related('author').prefetch_related('replies__author', 'likes')

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return SuccessResponse(
            data={'results': serializer.data, 'count': queryset.count()},
            message="Comments retrieved successfully"
        )

    def create(self, request, *args, **kwargs):
        issue_id = self.kwargs.get('issue_pk')
        issue = get_object_or_404(Issue, pk=issue_id)
        
        serializer = CommentCreateSerializer(data=request.data)
        if serializer.is_valid():
            comment = serializer.save(issue=issue, author=request.user)
            issue.update_comment_count()
            
            output_serializer = CommentSerializer(comment, context={'request': request})
            return SuccessResponse(
                data=output_serializer.data,
                message="Comment added successfully",
                status_code=status.HTTP_201_CREATED
            )
        
        return ErrorResponse(
            error_message="Validation failed",
            error_details=serializer.errors,
            error_code="VALIDATION_ERROR"
        )

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        
        # Check if user is the author or admin
        if comment.author != request.user and not request.user.is_staff:
            return ErrorResponse(
                error_message="You do not have permission to delete this comment",
                error_code="PERMISSION_DENIED",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        issue = comment.issue
        comment.delete()
        issue.update_comment_count()
        
        return SuccessResponse(message="Comment deleted successfully")


class CommentLikeView(views.APIView):
    """
    Toggle like on a comment.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        like, created = CommentLike.objects.get_or_create(
            user=request.user,
            comment=comment
        )
        
        if not created:
            like.delete()
            comment.update_like_count()
            return SuccessResponse(
                data={'liked': False, 'likes': comment.like_count},
                message="Like removed"
            )
        
        comment.update_like_count()
        return SuccessResponse(
            data={'liked': True, 'likes': comment.like_count},
            message="Comment liked"
        )
