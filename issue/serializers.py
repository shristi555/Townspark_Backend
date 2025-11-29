from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Issue

User = get_user_model()


class UserMinimalSerializer(serializers.ModelSerializer):
    """
    Minimal user serializer for nested representation in Issue responses.
    Only includes id and email as per impl.md requirements.
    """

    class Meta:
        model = User
        fields = ("id", "email")
        read_only_fields = ("id", "email")


class IssueSerializer(serializers.ModelSerializer):
    """
    Serializer for Issue model.
    
    Used for: Create, Retrieve, Update operations
    Returns nested user objects for created_by and resolved_by.
    """
    created_by = UserMinimalSerializer(read_only=True)
    resolved_by = UserMinimalSerializer(read_only=True)

    class Meta:
        model = Issue
        fields = (
            "id",
            "title",
            "description",
            "status",
            "created_at",
            "updated_at",
            "created_by",
            "resolved_by",
        )
        read_only_fields = ("id", "created_at", "updated_at", "created_by", "resolved_by")


class IssueCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new issue.
    
    Only requires title and description.
    Status defaults to 'open', created_by is set from request.user.
    """

    class Meta:
        model = Issue
        fields = ("id", "title", "description")
        read_only_fields = ("id",)

    def create(self, validated_data):
        """Create issue with the authenticated user as creator."""
        request = self.context.get("request")
        validated_data["created_by"] = request.user
        return super().create(validated_data)

    def to_representation(self, instance):
        """Return full issue representation after creation."""
        return IssueSerializer(instance, context=self.context).data


class IssueUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an issue.
    
    Allows updating: title, description, status
    Only staff can update status to 'resolved' and set resolved_by.
    """

    class Meta:
        model = Issue
        fields = ("id", "title", "description", "status")
        read_only_fields = ("id",)

    def validate_status(self, value):
        """Validate status changes based on user permissions."""
        request = self.context.get("request")
        user = request.user
        
        # Only staff or admin can set status to resolved
        if value == "resolved" and not (user.is_staff or user.is_admin):
            raise serializers.ValidationError(
                "Only staff members can mark issues as resolved."
            )
        return value

    def update(self, instance, validated_data):
        """Update issue and set resolved_by if status changed to resolved."""
        request = self.context.get("request")
        new_status = validated_data.get("status", instance.status)
        
        # If status is being changed to resolved, set resolved_by
        if new_status == "resolved" and instance.status != "resolved":
            validated_data["resolved_by"] = request.user
        # If reopening, clear resolved_by
        elif new_status == "open" and instance.status in ["resolved", "closed"]:
            validated_data["resolved_by"] = None
            
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Return full issue representation after update."""
        return IssueSerializer(instance, context=self.context).data


class IssueListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing issues.
    
    Same as IssueSerializer but optimized for list views.
    """
    created_by = UserMinimalSerializer(read_only=True)
    resolved_by = UserMinimalSerializer(read_only=True)

    class Meta:
        model = Issue
        fields = (
            "id",
            "title",
            "description",
            "status",
            "created_at",
            "updated_at",
            "created_by",
            "resolved_by",
        )
        read_only_fields = fields
