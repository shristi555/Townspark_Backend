from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Progress, ProgressImage
from issue.models import Issue

User = get_user_model()


class UserMinimalSerializer(serializers.ModelSerializer):
    """
    Minimal user serializer for nested representation.
    Only includes id and email.
    """

    class Meta:
        model = User
        fields = ("id", "email")
        read_only_fields = ("id", "email")


class IssueMinimalSerializer(serializers.ModelSerializer):
    """
    Minimal issue serializer for nested representation.
    Only includes id and title.
    """

    class Meta:
        model = Issue
        fields = ("id", "title")
        read_only_fields = ("id", "title")


class ProgressImageSerializer(serializers.ModelSerializer):
    """Serializer for progress images."""

    class Meta:
        model = ProgressImage
        fields = ("id", "image", "uploaded_at")
        read_only_fields = ("id", "uploaded_at")


class ProgressSerializer(serializers.ModelSerializer):
    """
    Serializer for Progress model.
    
    Used for: Retrieve operations
    Returns nested user and issue objects.
    """
    issue = IssueMinimalSerializer(read_only=True)
    updated_by = UserMinimalSerializer(read_only=True)
    images = ProgressImageSerializer(many=True, read_only=True)

    class Meta:
        model = Progress
        fields = (
            "id",
            "issue",
            "status",
            "notes",
            "updated_at",
            "updated_by",
            "images",
        )
        read_only_fields = ("id", "updated_at", "updated_by", "issue")


class ProgressCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new progress update.
    
    Only staff members can create progress updates.
    Requires issue_id, status. Notes and images are optional.
    """
    issue_id = serializers.IntegerField(write_only=True)
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Progress
        fields = ("id", "issue_id", "status", "notes", "images")
        read_only_fields = ("id",)

    def validate_issue_id(self, value):
        """Validate that the issue exists."""
        try:
            Issue.objects.get(pk=value)
        except Issue.DoesNotExist:
            raise serializers.ValidationError("Issue not found.")
        return value

    def validate(self, attrs):
        """Validate that the user is a staff member."""
        request = self.context.get("request")
        if not (request.user.is_staff or request.user.is_admin):
            raise serializers.ValidationError(
                "Only staff members can create progress updates."
            )
        return attrs

    def create(self, validated_data):
        """Create progress update with images."""
        request = self.context.get("request")
        issue_id = validated_data.pop("issue_id")
        images_data = validated_data.pop("images", [])
        
        # Get the issue
        issue = Issue.objects.get(pk=issue_id)
        
        # Create progress update
        progress = Progress.objects.create(
            issue=issue,
            updated_by=request.user,
            **validated_data
        )
        
        # Create progress images
        for image in images_data:
            ProgressImage.objects.create(progress=progress, image=image)
        
        return progress

    def to_representation(self, instance):
        """Return full progress representation after creation."""
        return ProgressSerializer(instance, context=self.context).data


class ProgressUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating a progress update.
    
    Allows updating: status, notes
    Only staff members can update progress.
    """
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Progress
        fields = ("id", "status", "notes", "images")
        read_only_fields = ("id",)

    def validate(self, attrs):
        """Validate that the user is a staff member."""
        request = self.context.get("request")
        if not (request.user.is_staff or request.user.is_admin):
            raise serializers.ValidationError(
                "Only staff members can update progress."
            )
        return attrs

    def update(self, instance, validated_data):
        """Update progress and add new images if provided."""
        images_data = validated_data.pop("images", [])
        
        # Update progress fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Add new images
        for image in images_data:
            ProgressImage.objects.create(progress=instance, image=image)
        
        return instance

    def to_representation(self, instance):
        """Return full progress representation after update."""
        return ProgressSerializer(instance, context=self.context).data


class ProgressListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing progress updates.
    
    Optimized for list views with minimal nested data.
    """
    issue = IssueMinimalSerializer(read_only=True)
    updated_by = UserMinimalSerializer(read_only=True)
    images = ProgressImageSerializer(many=True, read_only=True)

    class Meta:
        model = Progress
        fields = (
            "id",
            "issue",
            "status",
            "notes",
            "updated_at",
            "updated_by",
            "images",
        )
        read_only_fields = fields
