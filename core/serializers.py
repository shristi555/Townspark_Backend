from rest_framework import serializers
from .models import Category, Department, Badge


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'icon', 'description']


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'icon', 'description']


class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ['id', 'name', 'description', 'icon']


class StatusOptionSerializer(serializers.Serializer):
    """Serializer for status options."""
    id = serializers.CharField()
    name = serializers.CharField()
    color = serializers.CharField()
    icon = serializers.CharField()


class UrgencyLevelSerializer(serializers.Serializer):
    """Serializer for urgency levels."""
    id = serializers.CharField()
    name = serializers.CharField()
    color = serializers.CharField()
