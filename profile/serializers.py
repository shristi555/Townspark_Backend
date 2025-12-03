from django.contrib.auth import get_user_model
from rest_framework import serializers
from issue.models import Issue, Category
from progress.models import Progress

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile responses.
    Returns user object without sensitive information.
    """
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "full_name",
            "phone_number",
            "address",
            "profile_image",
            "is_staff",
            "is_admin",
            "date_joined",
        )
        read_only_fields = fields

    def get_profile_image(self, obj):
        """Return absolute URL for profile image."""
        request = self.context.get("request")
        if obj.profile_image:
            if request:
                return request.build_absolute_uri(obj.profile_image.url)
            return obj.profile_image.url
        return None


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile.
    Allows updating: full_name, phone_number, address, profile_image
    """
    profile_image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            "full_name",
            "phone_number",
            "address",
            "profile_image",
        )

    def to_representation(self, instance):
        """Use UserSerializer for response representation."""
        return UserSerializer(instance, context=self.context).data


class CategorySerializer(serializers.ModelSerializer):
    """Minimal category serializer for profile issue list."""

    class Meta:
        model = Category
        fields = ("id", "name")
        read_only_fields = fields


class IssueBasicSerializer(serializers.ModelSerializer):
    """
    Basic issue serializer for profile view.
    Returns minimal issue information.
    """
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Issue
        fields = (
            "id",
            "title",
            "location",
            "status",
            "created_at",
            "category",
        )
        read_only_fields = fields


class ProfileSerializer(serializers.ModelSerializer):
    """
    Full profile serializer with user info and stats.
    Returns user object with issues reported count, progress updates count,
    and list of issues reported.
    """
    profile_image = serializers.SerializerMethodField()
    issues_reported = serializers.SerializerMethodField()
    progress_updates = serializers.SerializerMethodField()
    issues = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "full_name",
            "phone_number",
            "address",
            "profile_image",
            "is_staff",
            "is_admin",
            "date_joined",
            "issues_reported",
            "progress_updates",
            "issues",
        )
        read_only_fields = fields

    def get_profile_image(self, obj):
        """Return absolute URL for profile image."""
        request = self.context.get("request")
        if obj.profile_image:
            if request:
                return request.build_absolute_uri(obj.profile_image.url)
            return obj.profile_image.url
        return None

    def get_issues_reported(self, obj):
        """Return the count of issues reported by the user."""
        return Issue.objects.filter(reported_by=obj).count()

    def get_progress_updates(self, obj):
        """Return the count of progress updates made by the user."""
        return Progress.objects.filter(updated_by=obj).count()

    def get_issues(self, obj):
        """Return the list of issues reported by the user with basic info."""
        issues = Issue.objects.filter(reported_by=obj).select_related("category").order_by("-created_at")
        return IssueBasicSerializer(issues, many=True, context=self.context).data
