from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    
    Request: email, password, full_name (optional), phone_number (optional), 
             address (optional), profile_image (optional)
    Response: User object without password
    """
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    full_name = serializers.CharField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    profile_image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "password",
            "full_name",
            "phone_number",
            "address",
            "profile_image",
        )
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": True},
        }

    def create(self, validated_data):
        """Create a new user with encrypted password."""
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile responses.
    
    Returns user object without sensitive information.
    Used for: GET /auth/users/me/, registration response, login response
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
        )
        read_only_fields = ("id", "email")

    def get_profile_image(self, obj):
        """Return absolute URL for profile image."""
        request = self.context.get("request")
        if obj.profile_image:
            if request:
                return request.build_absolute_uri(obj.profile_image.url)
            return obj.profile_image.url
        return None


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile.
    
    Allows updating: full_name, phone_number, address, profile_image
    """
    profile_image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "full_name",
            "phone_number",
            "address",
            "profile_image",
        )
        read_only_fields = ("id", "email")

    def to_representation(self, instance):
        """Use UserSerializer for response representation."""
        return UserSerializer(instance, context=self.context).data


class PublicUserSerializer(serializers.ModelSerializer):
    """
    Serializer for public user information.
    
    Only exposes: full_name, address, profile_image
    Used for public profile lookups.
    """
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("full_name", "address", "profile_image")

    def get_profile_image(self, obj):
        """Return absolute URL for profile image."""
        request = self.context.get("request")
        if obj.profile_image:
            if request:
                return request.build_absolute_uri(obj.profile_image.url)
            return obj.profile_image.url
        return None


class LoginSerializer(serializers.Serializer):
    """Serializer for login request validation."""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
