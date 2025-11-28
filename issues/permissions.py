from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only to the owner
        if hasattr(obj, 'reporter'):
            return obj.reporter == request.user
        if hasattr(obj, 'author'):
            return obj.author == request.user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False


class IsResolverOrAdmin(permissions.BasePermission):
    """
    Permission to check if user is a resolver or admin.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Admins always have permission
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # Check if user has resolver role
        if hasattr(request.user, 'role') and request.user.role == 'resolver':
            return True
        
        # Check if user has resolver profile
        if hasattr(request.user, 'resolver_profile'):
            return request.user.resolver_profile.is_verified
        
        return False


class IsResolver(permissions.BasePermission):
    """
    Permission to check if user is a verified resolver.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if hasattr(request.user, 'role') and request.user.role == 'resolver':
            return True
        
        if hasattr(request.user, 'resolver_profile'):
            return request.user.resolver_profile.is_verified
        
        return False


class IsAdminOrResolver(permissions.BasePermission):
    """
    Permission for admin or resolver specific actions.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return (
            request.user.is_staff or 
            request.user.is_superuser or
            (hasattr(request.user, 'role') and request.user.role == 'resolver')
        )
