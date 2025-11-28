from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import (
    Issue, IssueImage, IssueTimeline, OfficialResponse,
    Comment, Upvote, Bookmark
)
from core.serializers import CategorySerializer, DepartmentSerializer

User = get_user_model()


class UserMinimalSerializer(serializers.ModelSerializer):
    """Minimal user info for nested serialization."""
    name = serializers.CharField(source='full_name')
    avatar = serializers.SerializerMethodField()
    is_resolver = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'name', 'avatar', 'is_resolver', 'is_admin']

    def get_avatar(self, obj):
        request = self.context.get('request')
        if obj.profile_image and request:
            return request.build_absolute_uri(obj.profile_image.url)
        return None

    def get_is_resolver(self, obj):
        return getattr(obj, 'role', None) == 'resolver'

    def get_is_admin(self, obj):
        return obj.is_staff or obj.is_superuser


class IssueImageSerializer(serializers.ModelSerializer):
    """Serializer for issue images."""
    url = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = IssueImage
        fields = ['id', 'url', 'thumbnail', 'is_after_image', 'uploaded_at']

    def get_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_thumbnail(self, obj):
        # For now, return the same URL. In production, you'd generate thumbnails
        return self.get_url(obj)


class IssueTimelineSerializer(serializers.ModelSerializer):
    """Serializer for issue timeline entries."""
    updated_by = UserMinimalSerializer(read_only=True)
    date = serializers.DateTimeField(source='created_at')

    class Meta:
        model = IssueTimeline
        fields = ['status', 'date', 'note', 'updated_by']


class OfficialResponseSerializer(serializers.ModelSerializer):
    """Serializer for official responses."""
    department = serializers.CharField(source='department.name', read_only=True)
    responder = UserMinimalSerializer(read_only=True)
    date = serializers.DateTimeField(source='created_at')

    class Meta:
        model = OfficialResponse
        fields = ['department', 'message', 'date', 'responder']


class CommentReplySerializer(serializers.ModelSerializer):
    """Serializer for comment replies (nested)."""
    author = UserMinimalSerializer(read_only=True)
    likes = serializers.IntegerField(source='like_count')

    class Meta:
        model = Comment
        fields = ['id', 'author', 'content', 'likes', 'created_at']


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comments with replies."""
    author = UserMinimalSerializer(read_only=True)
    likes = serializers.IntegerField(source='like_count')
    replies = CommentReplySerializer(many=True, read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'author', 'content', 'likes', 'is_liked', 'created_at', 'replies']

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False


class CommentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating comments."""
    parent_id = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = Comment
        fields = ['content', 'parent_id']

    def create(self, validated_data):
        parent_id = validated_data.pop('parent_id', None)
        if parent_id:
            validated_data['parent_id'] = parent_id
        return super().create(validated_data)


class IssueListSerializer(serializers.ModelSerializer):
    """Compact serializer for issue lists."""
    author = UserMinimalSerializer(source='reporter', read_only=True)
    upvotes = serializers.IntegerField(source='upvote_count')
    uplifts = serializers.IntegerField(source='upvote_count')
    comments = serializers.IntegerField(source='comment_count')
    location = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    category = serializers.CharField(source='category_id')
    is_upvoted = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()

    class Meta:
        model = Issue
        fields = [
            'id', 'title', 'description', 'category', 'status', 'urgency',
            'location', 'images', 'author', 'upvotes', 'uplifts', 'comments',
            'is_upvoted', 'is_bookmarked', 'created_at'
        ]

    def get_location(self, obj):
        return f"{obj.address}, {obj.area}"

    def get_images(self, obj):
        request = self.context.get('request')
        images = obj.images.filter(is_after_image=False)[:1]  # Get first image
        return [request.build_absolute_uri(img.image.url) for img in images if img.image and request]

    def get_is_upvoted(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.upvotes.filter(user=request.user).exists()
        return False

    def get_is_bookmarked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.bookmarks.filter(user=request.user).exists()
        return False


class IssueDetailSerializer(serializers.ModelSerializer):
    """Full serializer for issue details."""
    author = UserMinimalSerializer(source='reporter', read_only=True)
    reporter = UserMinimalSerializer(read_only=True)
    assigned_resolver = UserMinimalSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    category = serializers.CharField(source='category_id')
    upvotes = serializers.IntegerField(source='upvote_count')
    uplifts = serializers.IntegerField(source='upvote_count')
    comments = serializers.IntegerField(source='comment_count')
    shares = serializers.IntegerField(source='share_count')
    location = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    after_images = serializers.SerializerMethodField()
    timeline = IssueTimelineSerializer(many=True, read_only=True)
    official_response = serializers.SerializerMethodField()
    is_upvoted = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()

    class Meta:
        model = Issue
        fields = [
            'id', 'title', 'description', 'category', 'status', 'urgency',
            'location', 'images', 'after_images', 'author', 'reporter',
            'assigned_resolver', 'department', 'upvotes', 'uplifts', 'comments',
            'shares', 'is_upvoted', 'is_bookmarked', 'is_anonymous',
            'created_at', 'updated_at', 'resolved_at', 'timeline', 'official_response'
        ]

    def get_location(self, obj):
        return {
            'address': obj.address,
            'area': obj.area,
            'coordinates': {
                'lat': float(obj.latitude) if obj.latitude else None,
                'lng': float(obj.longitude) if obj.longitude else None
            }
        }

    def get_images(self, obj):
        request = self.context.get('request')
        images = obj.images.filter(is_after_image=False)
        return [request.build_absolute_uri(img.image.url) for img in images if img.image and request]

    def get_after_images(self, obj):
        request = self.context.get('request')
        images = obj.images.filter(is_after_image=True)
        return [request.build_absolute_uri(img.image.url) for img in images if img.image and request]

    def get_official_response(self, obj):
        try:
            response = obj.official_response
            return OfficialResponseSerializer(response, context=self.context).data
        except OfficialResponse.DoesNotExist:
            return None

    def get_is_upvoted(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.upvotes.filter(user=request.user).exists()
        return False

    def get_is_bookmarked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.bookmarks.filter(user=request.user).exists()
        return False


class IssueCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating issues."""
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )
    latitude = serializers.DecimalField(
        max_digits=9, decimal_places=6, required=False, allow_null=True
    )
    longitude = serializers.DecimalField(
        max_digits=9, decimal_places=6, required=False, allow_null=True
    )

    class Meta:
        model = Issue
        fields = [
            'title', 'description', 'category', 'urgency', 'address', 'area',
            'latitude', 'longitude', 'department', 'is_anonymous', 'images'
        ]

    def create(self, validated_data):
        images = validated_data.pop('images', [])
        issue = Issue.objects.create(**validated_data)
        
        # Create initial timeline entry
        IssueTimeline.objects.create(
            issue=issue,
            status=Issue.Status.REPORTED,
            note="Issue reported",
            updated_by=issue.reporter
        )
        
        # Save images
        for image in images[:5]:  # Max 5 images
            IssueImage.objects.create(issue=issue, image=image)
        
        return issue


class IssueUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating issues."""
    class Meta:
        model = Issue
        fields = ['title', 'description', 'urgency', 'address', 'area', 'latitude', 'longitude']


class IssueStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating issue status."""
    status = serializers.ChoiceField(choices=Issue.Status.choices)
    note = serializers.CharField(required=False, allow_blank=True)


class IssueAssignSerializer(serializers.Serializer):
    """Serializer for assigning issues to resolvers."""
    resolver_id = serializers.IntegerField()


class OfficialResponseCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating official responses."""
    class Meta:
        model = OfficialResponse
        fields = ['message']
