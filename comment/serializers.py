from rest_framework import serializers
from .models import Comment


class UserMinimalSerializer(serializers.Serializer):
    """Minimal user serializer for comment responses."""
    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(read_only=True)


class IssueMinimalSerializer(serializers.Serializer):
    """Minimal issue serializer for comment responses."""
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(read_only=True)


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment model with full nested user and issue info.
    Used for standard CRUD operations.
    """
    user = UserMinimalSerializer(read_only=True)
    issue = IssueMinimalSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ["id", "issue", "user", "content", "created_at"]
        read_only_fields = ["id", "created_at"]


class CommentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating comments.
    Expects issue ID in the request body.
    """
    issue_id = serializers.IntegerField(write_only=True)
    user = UserMinimalSerializer(read_only=True)
    issue = IssueMinimalSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ["id", "issue_id", "issue", "user", "content", "created_at"]
        read_only_fields = ["id", "created_at"]
    
    def validate_issue_id(self, value):
        from issue.models import Issue
        if not Issue.objects.filter(id=value).exists():
            raise serializers.ValidationError("Issue with this ID does not exist.")
        return value
    
    def create(self, validated_data):
        from issue.models import Issue
        issue_id = validated_data.pop("issue_id")
        issue = Issue.objects.get(id=issue_id)
        validated_data["issue"] = issue
        return super().create(validated_data)


class CommentUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating comments.
    Only content can be updated.
    """
    user = UserMinimalSerializer(read_only=True)
    issue = IssueMinimalSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ["id", "issue", "user", "content", "created_at"]
        read_only_fields = ["id", "issue", "user", "created_at"]


class CommentMineSerializer(serializers.ModelSerializer):
    """
    Serializer for listing user's own comments.
    Excludes user field as it's always the authenticated user.
    """
    issue = IssueMinimalSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ["id", "issue", "content", "created_at"]
        read_only_fields = ["id", "issue", "created_at"]
