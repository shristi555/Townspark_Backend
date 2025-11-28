from rest_framework import viewsets, views, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Notification
from .serializers import NotificationSerializer
from core.utils.response_models import SuccessResponse, ErrorResponse


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Notification operations.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'patch', 'delete']

    def get_queryset(self):
        queryset = Notification.objects.filter(
            user=self.request.user
        ).select_related('issue', 'actor')
        
        # Filter by read status
        read_param = self.request.query_params.get('read')
        if read_param is not None:
            read = read_param.lower() == 'true'
            queryset = queryset.filter(read=read)
        
        # Filter by type
        type_param = self.request.query_params.get('type')
        if type_param:
            queryset = queryset.filter(type=type_param)
        
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        unread_count = queryset.filter(read=False).count()
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response_data = self.get_paginated_response(serializer.data).data
            response_data['data']['unread_count'] = unread_count
            return SuccessResponse(
                data={
                    'results': serializer.data,
                    'count': queryset.count(),
                    'unread_count': unread_count
                },
                message="Notifications retrieved successfully"
            )
        
        serializer = self.get_serializer(queryset, many=True)
        return SuccessResponse(
            data={
                'results': serializer.data,
                'count': queryset.count(),
                'unread_count': unread_count
            },
            message="Notifications retrieved successfully"
        )

    def destroy(self, request, *args, **kwargs):
        notification = self.get_object()
        notification.delete()
        return SuccessResponse(message="Notification deleted successfully")

    @action(detail=True, methods=['patch'], url_path='read')
    def mark_read(self, request, pk=None):
        """Mark a notification as read."""
        notification = self.get_object()
        notification.read = True
        notification.save(update_fields=['read'])
        
        serializer = self.get_serializer(notification)
        return SuccessResponse(
            data=serializer.data,
            message="Notification marked as read"
        )

    @action(detail=False, methods=['post'], url_path='read-all')
    def mark_all_read(self, request):
        """Mark all notifications as read."""
        count = Notification.objects.filter(
            user=request.user,
            read=False
        ).update(read=True)
        
        return SuccessResponse(
            data={'marked_count': count},
            message=f"{count} notifications marked as read"
        )
