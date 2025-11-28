from rest_framework import viewsets, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import Category, Department
from .serializers import CategorySerializer, DepartmentSerializer
from .utils.response_models import SuccessResponse


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing categories.
    """
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return SuccessResponse(data=serializer.data, message="Categories retrieved successfully")


class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing departments.
    """
    queryset = Department.objects.filter(is_active=True)
    serializer_class = DepartmentSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return SuccessResponse(data=serializer.data, message="Departments retrieved successfully")


class StatusOptionsView(views.APIView):
    """
    Get all status options.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        status_options = [
            {"id": "reported", "name": "Reported", "color": "status-reported", "icon": "report"},
            {"id": "acknowledged", "name": "Acknowledged", "color": "status-acknowledged", "icon": "verified_user"},
            {"id": "in-progress", "name": "In Progress", "color": "status-progress", "icon": "hourglass_top"},
            {"id": "resolved", "name": "Resolved", "color": "status-resolved", "icon": "task_alt"},
        ]
        return SuccessResponse(data=status_options, message="Status options retrieved successfully")


class UrgencyLevelsView(views.APIView):
    """
    Get all urgency levels.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        urgency_levels = [
            {"id": "low", "name": "Low", "color": "urgency-low"},
            {"id": "normal", "name": "Normal", "color": "urgency-normal"},
            {"id": "high", "name": "High", "color": "urgency-high"},
            {"id": "critical", "name": "Critical", "color": "urgency-critical"},
        ]
        return SuccessResponse(data=urgency_levels, message="Urgency levels retrieved successfully")


class PlatformStatsView(views.APIView):
    """
    Get public platform statistics (for landing page).
    """
    permission_classes = [AllowAny]

    def get(self, request):
        from issues.models import Issue
        from django.contrib.auth import get_user_model
        from django.db.models import Avg, F, ExpressionWrapper, DurationField
        
        User = get_user_model()
        
        total_issues = Issue.objects.count()
        resolved_issues = Issue.objects.filter(status='resolved').count()
        active_members = User.objects.filter(is_active=True).count()
        
        # Calculate average resolution time
        resolved_with_time = Issue.objects.filter(
            status='resolved', 
            resolved_at__isnull=False
        ).annotate(
            resolution_time=ExpressionWrapper(
                F('resolved_at') - F('created_at'),
                output_field=DurationField()
            )
        )
        
        avg_resolution = resolved_with_time.aggregate(avg=Avg('resolution_time'))['avg']
        if avg_resolution:
            hours = int(avg_resolution.total_seconds() // 3600)
            avg_resolution_time = f"{hours}h"
        else:
            avg_resolution_time = "N/A"
        
        stats = {
            "issues_reported": total_issues,
            "issues_resolved": resolved_issues,
            "active_members": active_members,
            "avg_resolution_time": avg_resolution_time
        }
        
        return SuccessResponse(data=stats, message="Platform statistics retrieved successfully")
