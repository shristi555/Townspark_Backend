from rest_framework.response import Response
from rest_framework import status, views, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from core.utils.response_models import SuccessResponse, ErrorResponse
from .serializers import (
    UserSerializer, UserUpdateSerializer, ResolverCreateSerializer,
    ResolverDetailSerializer, UserSettingsSerializer
)
from .models import ResolverProfile, UserRole

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
            return SuccessResponse(
                data={"tokens": tokensData, "user": userData},
                message="Login successful"
            )

        else:
            return ErrorResponse(
                error_message="Authentication failed",
                error_details={
                    "detail": "Unable to authenticate with provided credentials."
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )


class UserMeView(views.APIView):
    """
    View for getting and updating the current user profile.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return SuccessResponse(data=serializer.data, message="User profile retrieved successfully")

    def patch(self, request):
        serializer = UserUpdateSerializer(
            request.user, 
            data=request.data, 
            partial=True,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            output_serializer = UserSerializer(request.user, context={'request': request})
            return SuccessResponse(
                data=output_serializer.data,
                message="Profile updated successfully"
            )
        return ErrorResponse(
            error_message="Validation failed",
            error_details=serializer.errors,
            error_code="VALIDATION_ERROR"
        )


class UserIssuesView(views.APIView):
    """
    View for getting current user's issues.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from issues.models import Issue
        from issues.serializers import IssueListSerializer
        
        queryset = Issue.objects.filter(reporter=request.user)
        
        # Filter by status
        status_param = request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        serializer = IssueListSerializer(queryset, many=True, context={'request': request})
        return SuccessResponse(
            data={'results': serializer.data, 'count': queryset.count()},
            message="User issues retrieved successfully"
        )


class UserBookmarksView(views.APIView):
    """
    View for getting current user's bookmarked issues.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from issues.models import Bookmark
        from issues.serializers import IssueListSerializer
        
        bookmarks = Bookmark.objects.filter(user=request.user).select_related('issue')
        issues = [b.issue for b in bookmarks]
        
        serializer = IssueListSerializer(issues, many=True, context={'request': request})
        return SuccessResponse(
            data={'results': serializer.data, 'count': len(issues)},
            message="Bookmarked issues retrieved successfully"
        )


class UserUpvotedView(views.APIView):
    """
    View for getting issues upvoted by current user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from issues.models import Upvote
        from issues.serializers import IssueListSerializer
        
        upvotes = Upvote.objects.filter(user=request.user).select_related('issue')
        issues = [u.issue for u in upvotes]
        
        serializer = IssueListSerializer(issues, many=True, context={'request': request})
        return SuccessResponse(
            data={'results': serializer.data, 'count': len(issues)},
            message="Upvoted issues retrieved successfully"
        )


class UserSettingsView(views.APIView):
    """
    View for getting and updating user settings.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Default settings structure
        settings = {
            "notifications": {
                "email": True,
                "push": True,
                "status_updates": True,
                "comments": True,
                "mentions": True
            },
            "privacy": {
                "profile_visible": True,
                "show_email": False
            },
            "preferences": {
                "dark_mode": False,
                "language": "en"
            }
        }
        return SuccessResponse(data=settings, message="Settings retrieved successfully")

    def patch(self, request):
        # For now, just acknowledge the update
        # In a real implementation, you'd save these to a UserSettings model
        return SuccessResponse(data=request.data, message="Settings updated successfully")


class UserProfileView(views.APIView):
    """
    View for getting a user's public profile.
    """
    permission_classes = [AllowAny]

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user, context={'request': request})
        return SuccessResponse(data=serializer.data, message="User profile retrieved successfully")


class ResolverRegisterView(views.APIView):
    """
    View for resolver registration.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResolverCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            return SuccessResponse(
                data={
                    "user": {
                        "id": user.id,
                        "name": user.full_name,
                        "email": user.email,
                        "role": user.role
                    },
                    "verification_status": "pending"
                },
                message="Registration successful. Your account is pending verification.",
                status_code=status.HTTP_201_CREATED
            )
        
        return ErrorResponse(
            error_message="Validation failed",
            error_details=serializer.errors,
            error_code="VALIDATION_ERROR"
        )


# Resolver Dashboard Views
class ResolverDashboardView(views.APIView):
    """
    View for resolver dashboard data.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from issues.models import Issue
        from issues.serializers import IssueListSerializer
        
        user = request.user
        
        # Check if user is a resolver
        if user.role != UserRole.RESOLVER and not user.is_staff:
            return ErrorResponse(
                error_message="Access denied",
                error_code="PERMISSION_DENIED",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        # Get stats
        if hasattr(user, 'resolver_profile'):
            stats = user.resolver_profile.get_stats()
        else:
            stats = {
                "pending": 0,
                "in_progress": 0,
                "resolved_this_month": 0,
                "avg_response_time": "N/A"
            }
        
        # Get assigned issues
        assigned_issues = Issue.objects.filter(
            assigned_resolver=user
        ).exclude(status='resolved')[:10]
        
        # Get pending issues (in resolver's jurisdiction)
        pending_issues = Issue.objects.filter(
            status='reported'
        )[:10]
        
        assigned_serializer = IssueListSerializer(
            assigned_issues, many=True, context={'request': request}
        )
        pending_serializer = IssueListSerializer(
            pending_issues, many=True, context={'request': request}
        )
        
        return SuccessResponse(
            data={
                "stats": stats,
                "assigned_issues": assigned_serializer.data,
                "pending_issues": pending_serializer.data
            },
            message="Dashboard data retrieved successfully"
        )


class ResolverAssignedView(views.APIView):
    """
    View for getting issues assigned to the current resolver.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from issues.models import Issue
        from issues.serializers import IssueListSerializer
        
        user = request.user
        
        if user.role != UserRole.RESOLVER and not user.is_staff:
            return ErrorResponse(
                error_message="Access denied",
                error_code="PERMISSION_DENIED",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        queryset = Issue.objects.filter(assigned_resolver=user)
        
        # Filter by status
        status_param = request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Filter by urgency
        urgency_param = request.query_params.get('urgency')
        if urgency_param:
            queryset = queryset.filter(urgency=urgency_param)
        
        serializer = IssueListSerializer(queryset, many=True, context={'request': request})
        return SuccessResponse(
            data={'results': serializer.data, 'count': queryset.count()},
            message="Assigned issues retrieved successfully"
        )


class ResolverPendingView(views.APIView):
    """
    View for getting pending issues in resolver's jurisdiction.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from issues.models import Issue
        from issues.serializers import IssueListSerializer
        
        user = request.user
        
        if user.role != UserRole.RESOLVER and not user.is_staff:
            return ErrorResponse(
                error_message="Access denied",
                error_code="PERMISSION_DENIED",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        # Get pending issues (not yet assigned)
        queryset = Issue.objects.filter(
            status='reported',
            assigned_resolver__isnull=True
        )
        
        serializer = IssueListSerializer(queryset, many=True, context={'request': request})
        return SuccessResponse(
            data={'results': serializer.data, 'count': queryset.count()},
            message="Pending issues retrieved successfully"
        )


class ResolverAcceptIssueView(views.APIView):
    """
    View for a resolver to accept/claim an issue.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        from issues.models import Issue, IssueTimeline
        
        user = request.user
        
        if user.role != UserRole.RESOLVER and not user.is_staff:
            return ErrorResponse(
                error_message="Access denied",
                error_code="PERMISSION_DENIED",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        issue = get_object_or_404(Issue, pk=pk)
        
        if issue.assigned_resolver:
            return ErrorResponse(
                error_message="Issue already assigned",
                error_code="ALREADY_ASSIGNED",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        issue.assigned_resolver = user
        issue.status = Issue.Status.ACKNOWLEDGED
        issue.save()
        
        # Create timeline entry
        IssueTimeline.objects.create(
            issue=issue,
            status=Issue.Status.ACKNOWLEDGED,
            note=f"Issue accepted by {user.full_name}",
            updated_by=user
        )
        
        return SuccessResponse(
            data={'id': issue.id, 'status': issue.status},
            message="Issue accepted successfully"
        )


class ResolverCompleteIssueView(views.APIView):
    """
    View for a resolver to mark an issue as resolved.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        from issues.models import Issue, IssueTimeline, IssueImage
        from django.utils import timezone
        
        user = request.user
        
        if user.role != UserRole.RESOLVER and not user.is_staff:
            return ErrorResponse(
                error_message="Access denied",
                error_code="PERMISSION_DENIED",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        issue = get_object_or_404(Issue, pk=pk)
        
        if issue.assigned_resolver != user and not user.is_staff:
            return ErrorResponse(
                error_message="You are not assigned to this issue",
                error_code="PERMISSION_DENIED",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        resolution_note = request.data.get('resolution_note', '')
        after_images = request.FILES.getlist('after_images', [])
        
        # Update issue
        issue.status = Issue.Status.RESOLVED
        issue.resolved_at = timezone.now()
        issue.save()
        
        # Create timeline entry
        IssueTimeline.objects.create(
            issue=issue,
            status=Issue.Status.RESOLVED,
            note=resolution_note or "Issue resolved",
            updated_by=user
        )
        
        # Save after images
        for image in after_images:
            IssueImage.objects.create(
                issue=issue,
                image=image,
                is_after_image=True
            )
        
        return SuccessResponse(
            data={'id': issue.id, 'status': issue.status},
            message="Issue marked as resolved"
        )


# Admin Views
class AdminDashboardView(views.APIView):
    """
    View for admin dashboard data.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        from issues.models import Issue
        from django.db.models import Avg, F, ExpressionWrapper, DurationField
        from django.utils import timezone
        
        # Stats
        total_users = User.objects.filter(role=UserRole.CITIZEN).count()
        active_resolvers = User.objects.filter(role=UserRole.RESOLVER, is_active=True).count()
        total_issues = Issue.objects.count()
        resolved_issues = Issue.objects.filter(status='resolved').count()
        pending_verification = ResolverProfile.objects.filter(is_verified=False).count()
        
        # Average resolution time
        resolved_with_time = Issue.objects.filter(
            status='resolved',
            resolved_at__isnull=False
        ).annotate(
            resolution_time=ExpressionWrapper(
                F('resolved_at') - F('created_at'),
                output_field=DurationField()
            )
        )
        
        avg_time = resolved_with_time.aggregate(avg=Avg('resolution_time'))['avg']
        if avg_time:
            hours = int(avg_time.total_seconds() // 3600)
            avg_resolution_time = f"{hours}h"
        else:
            avg_resolution_time = "N/A"
        
        return SuccessResponse(
            data={
                "stats": {
                    "total_users": total_users,
                    "active_resolvers": active_resolvers,
                    "total_issues": total_issues,
                    "resolved_issues": resolved_issues,
                    "pending_verification": pending_verification,
                    "avg_resolution_time": avg_resolution_time
                }
            },
            message="Admin dashboard data retrieved successfully"
        )


class AdminUsersView(views.APIView):
    """
    View for listing all users (citizens).
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        queryset = User.objects.filter(role=UserRole.CITIZEN)
        
        # Search
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(full_name__icontains=search) |
                models.Q(email__icontains=search)
            )
        
        # Filter by status
        status_param = request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(is_active=(status_param == 'active'))
        
        serializer = UserSerializer(queryset, many=True, context={'request': request})
        
        # Stats
        stats = {
            "total": User.objects.filter(role=UserRole.CITIZEN).count(),
            "active": User.objects.filter(role=UserRole.CITIZEN, is_active=True).count(),
            "suspended": User.objects.filter(role=UserRole.CITIZEN, is_active=False).count()
        }
        
        return SuccessResponse(
            data={
                'results': serializer.data,
                'count': queryset.count(),
                'stats': stats
            },
            message="Users retrieved successfully"
        )


class AdminUserDetailView(views.APIView):
    """
    View for getting/updating/deleting a specific user.
    """
    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user, context={'request': request})
        return SuccessResponse(data=serializer.data, message="User retrieved successfully")

    def patch(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            output_serializer = UserSerializer(user, context={'request': request})
            return SuccessResponse(data=output_serializer.data, message="User updated successfully")
        return ErrorResponse(
            error_message="Validation failed",
            error_details=serializer.errors,
            error_code="VALIDATION_ERROR"
        )

    def delete(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.delete()
        return SuccessResponse(message="User deleted successfully")


class AdminUserToggleStatusView(views.APIView):
    """
    View for toggling user active status.
    """
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        is_active = request.data.get('is_active', not user.is_active)
        user.is_active = is_active
        user.save()
        
        return SuccessResponse(
            data={'id': user.id, 'is_active': user.is_active},
            message=f"User {'activated' if user.is_active else 'deactivated'} successfully"
        )


class AdminResolversView(views.APIView):
    """
    View for listing all resolvers.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        queryset = User.objects.filter(role=UserRole.RESOLVER).select_related('resolver_profile')
        
        serializer = ResolverDetailSerializer(queryset, many=True, context={'request': request})
        
        # Stats
        stats = {
            "total": queryset.count(),
            "verified": queryset.filter(resolver_profile__is_verified=True).count(),
            "pending": queryset.filter(resolver_profile__is_verified=False).count()
        }
        
        return SuccessResponse(
            data={
                'results': serializer.data,
                'count': queryset.count(),
                'stats': stats
            },
            message="Resolvers retrieved successfully"
        )


class AdminResolversPendingView(views.APIView):
    """
    View for getting resolvers pending verification.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        queryset = User.objects.filter(
            role=UserRole.RESOLVER,
            resolver_profile__is_verified=False
        ).select_related('resolver_profile')
        
        serializer = ResolverDetailSerializer(queryset, many=True, context={'request': request})
        
        return SuccessResponse(
            data={'results': serializer.data, 'count': queryset.count()},
            message="Pending resolvers retrieved successfully"
        )


class AdminResolverVerifyView(views.APIView):
    """
    View for verifying a resolver.
    """
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        from django.utils import timezone
        
        user = get_object_or_404(User, pk=pk, role=UserRole.RESOLVER)
        
        if not hasattr(user, 'resolver_profile'):
            return ErrorResponse(
                error_message="Resolver profile not found",
                error_code="NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        approved = request.data.get('approved', True)
        
        if approved:
            user.resolver_profile.is_verified = True
            user.resolver_profile.verified_at = timezone.now()
            user.resolver_profile.verified_by = request.user
            user.resolver_profile.save()
            
            return SuccessResponse(
                data={'id': user.id, 'is_verified': True},
                message="Resolver verified successfully"
            )
        else:
            return SuccessResponse(
                data={'id': user.id, 'is_verified': False},
                message="Verification pending"
            )


class AdminResolverRejectView(views.APIView):
    """
    View for rejecting a resolver verification.
    """
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk, role=UserRole.RESOLVER)
        reason = request.data.get('reason', '')
        
        # Delete the user and profile
        user.delete()
        
        return SuccessResponse(
            message="Resolver rejected and removed"
        )


class AdminResolverDeleteView(views.APIView):
    """
    View for deleting a resolver.
    """
    permission_classes = [IsAdminUser]

    def delete(self, request, pk):
        user = get_object_or_404(User, pk=pk, role=UserRole.RESOLVER)
        user.delete()
        return SuccessResponse(message="Resolver deleted successfully")
