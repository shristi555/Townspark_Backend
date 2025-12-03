"""
Custom permissions for the issue app.

These permission classes can be used as decorators or in permission_classes
to restrict access to views based on user roles.
"""

from functools import wraps
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


class IsAdmin(BasePermission):
    """
    Permission class that allows access only to admin users.
    Checks if the user is authenticated and has is_admin=True.
    """
    message = "Only admin users can perform this action."

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_admin
        )


class IsStaff(BasePermission):
    """
    Permission class that allows access only to staff users.
    Checks if the user is authenticated and has is_staff=True.
    """
    message = "Only staff users can perform this action."

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_staff
        )


class IsAdminOrStaff(BasePermission):
    """
    Permission class that allows access to admin or staff users.
    Checks if the user is authenticated and has is_admin=True or is_staff=True.
    """
    message = "Only admin or staff users can perform this action."

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (request.user.is_admin or request.user.is_staff)
        )


class IsReporter(BasePermission):
    """
    Permission class that allows access only to the reporter of the issue.
    The view must have an `issue` attribute or `get_issue()` method.
    """
    message = "Only the reporter of the issue can perform this action."

    def has_object_permission(self, request, view, obj):
        # Check if obj is an Issue
        if hasattr(obj, 'reported_by'):
            return obj.reported_by == request.user
        # Check if obj has an issue attribute (e.g., Progress)
        if hasattr(obj, 'issue'):
            return obj.issue.reported_by == request.user
        return False


class IsReporterOrAdminOrStaff(BasePermission):
    """
    Permission class that allows access to the reporter, admin, or staff users.
    Used for updating issue status, adding progress updates, etc.
    """
    message = "Only the reporter, admin, or staff users can perform this action."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Admin or staff can always access
        if request.user.is_admin or request.user.is_staff:
            return True
        
        # Check if user is the reporter
        if hasattr(obj, 'reported_by'):
            return obj.reported_by == request.user
        if hasattr(obj, 'issue'):
            return obj.issue.reported_by == request.user
        
        return False


# Decorator-style permissions
def admin_access_only(view_func):
    """
    Decorator that restricts access to admin users only.
    
    Usage:
        @admin_access_only
        def my_view(self, request):
            ...
    """
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        if not request.user.is_admin:
            return Response(
                {"detail": "Only admin users can perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )
        return view_func(self, request, *args, **kwargs)
    return wrapper


def staff_access_only(view_func):
    """
    Decorator that restricts access to staff users only.
    
    Usage:
        @staff_access_only
        def my_view(self, request):
            ...
    """
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        if not request.user.is_staff:
            return Response(
                {"detail": "Only staff users can perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )
        return view_func(self, request, *args, **kwargs)
    return wrapper


def admin_or_staff_access_only(view_func):
    """
    Decorator that restricts access to admin or staff users only.
    
    Usage:
        @admin_or_staff_access_only
        def my_view(self, request):
            ...
    """
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        if not (request.user.is_admin or request.user.is_staff):
            return Response(
                {"detail": "Only admin or staff users can perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )
        return view_func(self, request, *args, **kwargs)
    return wrapper


def reporter_or_admin_staff(get_issue_func):
    """
    Decorator factory that restricts access to the reporter, admin, or staff users.
    
    Args:
        get_issue_func: A function that takes (self, request, *args, **kwargs) 
                       and returns the Issue object.
    
    Usage:
        @reporter_or_admin_staff(lambda self, request, issue_id: Issue.objects.get(pk=issue_id))
        def my_view(self, request, issue_id):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            if not request.user.is_authenticated:
                return Response(
                    {"detail": "Authentication credentials were not provided."},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Admin or staff can always access
            if request.user.is_admin or request.user.is_staff:
                return view_func(self, request, *args, **kwargs)
            
            # Get the issue and check if user is the reporter
            try:
                issue = get_issue_func(self, request, *args, **kwargs)
                if issue.reported_by == request.user:
                    return view_func(self, request, *args, **kwargs)
            except Exception:
                pass
            
            return Response(
                {"detail": "Only the reporter, admin, or staff users can perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )
        return wrapper
    return decorator


def reporter_only(get_issue_func):
    """
    Decorator factory that restricts access to the reporter only.
    
    Args:
        get_issue_func: A function that takes (self, request, *args, **kwargs) 
                       and returns the Issue object.
    
    Usage:
        @reporter_only(lambda self, request, issue_id: Issue.objects.get(pk=issue_id))
        def my_view(self, request, issue_id):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            if not request.user.is_authenticated:
                return Response(
                    {"detail": "Authentication credentials were not provided."},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Get the issue and check if user is the reporter
            try:
                issue = get_issue_func(self, request, *args, **kwargs)
                if issue.reported_by == request.user:
                    return view_func(self, request, *args, **kwargs)
            except Exception:
                pass
            
            return Response(
                {"detail": "Only the reporter of the issue can perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )
        return wrapper
    return decorator
