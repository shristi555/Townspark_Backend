from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Category, Issue, IssueImage

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


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category model (read-only).
    Used to represent categories in issue responses.
    """

    class Meta:
        model = Category
        fields = ("id", "name", "description")
        read_only_fields = ("id", "name", "description")


class CategoryCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new categories.
    Only admin users can create categories.
    """

    class Meta:
        model = Category
        fields = ("name", "description")

    def validate_name(self, value):
        """Validate that the category name is unique."""
        if Category.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("A category with this name already exists.")
        return value


class IssueImageSerializer(serializers.ModelSerializer):
    """Serializer for issue images."""

    class Meta:
        model = IssueImage
        fields = ("id", "image", "uploaded_at")
        read_only_fields = ("id", "uploaded_at")


class IssueSerializer(serializers.ModelSerializer):
    """
    Serializer for Issue model (read-only except status).
    Used for representing issues in detail views.
    """
    category = CategorySerializer(read_only=True)
    reported_by = MinimalUserSerializer(read_only=True)
    images = IssueImageSerializer(many=True, read_only=True)

    class Meta:
        model = Issue
        fields = (
            "id",
            "title",
            "description",
            "location",
            "images",
            "status",
            "created_at",
            "updated_at",
            "category",
            "reported_by",
        )
        read_only_fields = (
            "id",
            "title",
            "description",
            "location",
            "images",
            "created_at",
            "updated_at",
            "category",
            "reported_by",
        )


class IssueListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing issues (lighter version).
    Used for list views to reduce payload size.
    """
    category = CategorySerializer(read_only=True)
    reported_by = MinimalUserSerializer(read_only=True)
    image_count = serializers.SerializerMethodField()

    class Meta:
        model = Issue
        fields = (
            "id",
            "title",
            "description",
            "images",
            "location",
            "status",
            "created_at",
            "updated_at",
            "category",
            "reported_by",
            "image_count",
        )
        read_only_fields = fields

    def get_image_count(self, obj):
        """Get the count of images for the issue."""
        return obj.images.count()


class IssueCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new issues.
    Users provide title, description, location, category, and optional images.
    """
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
        allow_empty=True
    )


    class Meta:
        model = Issue
        fields = ("title", "description", "location", "category", "images")

    def create(self, validated_data):
        """Create a new issue with images."""
        images_data = validated_data.pop("images", [])
        request = self.context.get("request")
        
        # Create the issue
        issue = Issue.objects.create(
            reported_by=request.user,
            **validated_data
        )
        
        # Create issue images
        for image in images_data:
            IssueImage.objects.create(issue=issue, image=image)
        
        return issue

    def to_representation(self, instance):
        """Use IssueSerializer for response."""
        return IssueSerializer(instance, context=self.context).data


class IssueUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating issue status.
    Only admin/staff or the reporter can update the status.
    """

    class Meta:
        model = Issue
        fields = ("status",)

    def validate_status(self, value):
        """Validate that the status is a valid choice."""
        valid_statuses = [choice[0] for choice in Issue.STATUS_CHOICES]
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Invalid status. Valid choices are: {', '.join(valid_statuses)}"
            )
        return value

    def to_representation(self, instance):
        """Use IssueSerializer for response."""
        return IssueSerializer(instance, context=self.context).data
