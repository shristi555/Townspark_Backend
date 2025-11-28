from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Notification

User = get_user_model()


class ActorSerializer(serializers.ModelSerializer):
    """Minimal actor info for notifications."""
    name = serializers.CharField(source='full_name')
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'name', 'avatar']

    def get_avatar(self, obj):
        request = self.context.get('request')
        if obj.profile_image and request:
            return request.build_absolute_uri(obj.profile_image.url)
        return None


class IssueMinimalSerializer(serializers.Serializer):
    """Minimal issue info for notifications."""
    id = serializers.CharField()
    title = serializers.CharField()


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications."""
    issue = IssueMinimalSerializer(read_only=True)
    actor = ActorSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'type', 'title', 'message', 'issue', 'actor', 'read', 'created_at']
