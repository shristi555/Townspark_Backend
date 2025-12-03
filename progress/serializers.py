from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Progress, ProgressImage
from issue.models import Issue

User = get_user_model()


class MinimalUserSerializer(serializers.ModelSerializer):
    """
    Minimal user serializer for nested representation.
    Exposes only id, full_name, and profile_image.
    All fields are read-only.
    """

    class Meta:
        model = User
        fields = ("id", "full_name", "profile_image")
        read_only_fields = ("id", "full_name", "profile_image")


class ProgressImageSerializer(serializers.ModelSerializer):
    """Serializer for progress images."""

    class Meta:
        model = ProgressImage
        fields = ("id", "image", "uploaded_at")
        read_only_fields = ("id", "uploaded_at")


class ProgressSerializer(serializers.ModelSerializer):
    """
    Serializer for Progress model (read-only).
    Used for representing progress updates in responses.
    """
    updated_by = MinimalUserSerializer(read_only=True)
    images = ProgressImageSerializer(many=True, read_only=True)

    class Meta:
        model = Progress
        fields = (
            "id",
            "issue",
            "description",
            "created_at",
            "updated_by",
            "images",
        )
        read_only_fields = fields


class ProgressCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new progress update.
    
    Only the reporter, admin, or staff members can create progress updates.
    Requires issue (id), description. Images are optional.
    """
    issue = serializers.PrimaryKeyRelatedField(queryset=Issue.objects.all())
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
        allow_empty=True
    )

    class Meta:
        model = Progress
        fields = ("issue", "description", "images")

    def validate(self, attrs):
        """Validate that the user is allowed to add progress."""
        request = self.context.get("request")
        issue = attrs.get("issue")
        
        # Check if user is admin/staff or the reporter
        is_admin_staff = request.user.is_admin or request.user.is_staff
        is_reporter = issue.reported_by == request.user
        
        if not (is_admin_staff or is_reporter):
            raise serializers.ValidationError(
                "Only the reporter, admin, or staff can add progress updates."
            )
        
        return attrs

    def create(self, validated_data):
        """Create a new progress update with images."""
        images_data = validated_data.pop("images", [])
        request = self.context.get("request")
        
        # Create the progress update
        progress = Progress.objects.create(
            updated_by=request.user,
            **validated_data
        )
        
        # Create progress images
        for image in images_data:
            ProgressImage.objects.create(progress=progress, image=image)
        
        return progress

    def to_representation(self, instance):
        """Use ProgressSerializer for response."""
        return ProgressSerializer(instance, context=self.context).data
