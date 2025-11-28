from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from rest_framework import serializers

from .models import User, ResolverProfile, UserRole


class UserCreateSerializer(BaseUserCreateSerializer):
    full_name = serializers.CharField(required=True)
    profile_image = serializers.ImageField(
        required=False, allow_null=True
    )
    user_type = serializers.ChoiceField(
        choices=[('citizen', 'Citizen'), ('resolver', 'Resolver')],
        required=False,
        default='citizen',
        write_only=True
    )

    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = (
            "id",
            "email",
            "password",
            "full_name",
            "phone_number",
            "address",
            "profile_image",
            "user_type",
        )
        extra_kwargs = {"password": {"write_only": True}, "email": {"required": True}}

    def create(self, validated_data):
        user_type = validated_data.pop('user_type', 'citizen')
        if user_type == 'resolver':
            validated_data['role'] = UserRole.RESOLVER
        else:
            validated_data['role'] = UserRole.CITIZEN
        return super().create(validated_data)


class UserSerializer(BaseUserSerializer):
    profile_image = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    name = serializers.CharField(source='full_name', read_only=True)
    phone = serializers.CharField(source='phone_number', read_only=True)
    joined_at = serializers.DateTimeField(source='created_at', read_only=True)
    stats = serializers.SerializerMethodField()
    badges = serializers.SerializerMethodField()

    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = (
            "id",
            "email",
            "full_name",
            "name",
            "phone_number",
            "phone",
            "address",
            "ward",
            "bio",
            "location",
            "profile_image",
            "avatar",
            "role",
            "is_active",
            "joined_at",
            "stats",
            "badges",
        )

    def get_profile_image(self, obj):
        request = self.context.get("request")
        if obj.profile_image and request:
            return request.build_absolute_uri(obj.profile_image.url)
        return None

    def get_avatar(self, obj):
        return self.get_profile_image(obj)

    def get_stats(self, obj):
        return obj.get_stats()

    def get_badges(self, obj):
        return obj.get_badges()


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""
    name = serializers.CharField(source='full_name', required=False)
    phone = serializers.CharField(source='phone_number', required=False)

    class Meta:
        model = User
        fields = [
            'full_name', 'name', 'phone_number', 'phone', 
            'address', 'ward', 'bio', 'location', 'profile_image'
        ]


class ResolverProfileSerializer(serializers.ModelSerializer):
    """Serializer for resolver profile."""
    department = serializers.SerializerMethodField()
    stats = serializers.SerializerMethodField()

    class Meta:
        model = ResolverProfile
        fields = [
            'designation', 'employee_id', 'jurisdiction',
            'department', 'is_verified', 'verified_at', 'stats'
        ]

    def get_department(self, obj):
        if obj.department:
            return {
                'id': obj.department.id,
                'name': obj.department.name,
                'icon': obj.department.icon
            }
        return None

    def get_stats(self, obj):
        return obj.get_stats()


class ResolverCreateSerializer(serializers.Serializer):
    """Serializer for resolver registration."""
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20, required=False)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    department = serializers.CharField(max_length=50)
    employee_id = serializers.CharField(max_length=50)
    designation = serializers.CharField(max_length=100)
    id_document = serializers.FileField(required=False)

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })
        
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({
                "email": "This email is already registered."
            })
        
        if ResolverProfile.objects.filter(employee_id=data['employee_id']).exists():
            raise serializers.ValidationError({
                "employee_id": "This employee ID is already registered."
            })
        
        return data

    def create(self, validated_data):
        from core.models import Department
        
        # Create user
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data['name'],
            phone_number=validated_data.get('phone', ''),
            role=UserRole.RESOLVER
        )
        
        # Get department
        department = None
        try:
            department = Department.objects.get(id=validated_data['department'])
        except Department.DoesNotExist:
            pass
        
        # Create resolver profile
        ResolverProfile.objects.create(
            user=user,
            department=department,
            designation=validated_data['designation'],
            employee_id=validated_data['employee_id'],
            id_document=validated_data.get('id_document'),
            is_verified=False
        )
        
        return user


class ResolverDetailSerializer(serializers.ModelSerializer):
    """Full serializer for resolver details."""
    name = serializers.CharField(source='full_name')
    avatar = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    designation = serializers.SerializerMethodField()
    employee_id = serializers.SerializerMethodField()
    jurisdiction = serializers.SerializerMethodField()
    is_verified = serializers.SerializerMethodField()
    verified_at = serializers.SerializerMethodField()
    stats = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'name', 'email', 'avatar', 'role', 'department',
            'designation', 'employee_id', 'jurisdiction',
            'is_verified', 'verified_at', 'stats'
        ]

    def get_avatar(self, obj):
        request = self.context.get('request')
        if obj.profile_image and request:
            return request.build_absolute_uri(obj.profile_image.url)
        return None

    def get_department(self, obj):
        if hasattr(obj, 'resolver_profile') and obj.resolver_profile.department:
            dept = obj.resolver_profile.department
            return {'id': dept.id, 'name': dept.name, 'icon': dept.icon}
        return None

    def get_designation(self, obj):
        if hasattr(obj, 'resolver_profile'):
            return obj.resolver_profile.designation
        return None

    def get_employee_id(self, obj):
        if hasattr(obj, 'resolver_profile'):
            return obj.resolver_profile.employee_id
        return None

    def get_jurisdiction(self, obj):
        if hasattr(obj, 'resolver_profile'):
            return obj.resolver_profile.jurisdiction
        return None

    def get_is_verified(self, obj):
        if hasattr(obj, 'resolver_profile'):
            return obj.resolver_profile.is_verified
        return False

    def get_verified_at(self, obj):
        if hasattr(obj, 'resolver_profile') and obj.resolver_profile.verified_at:
            return obj.resolver_profile.verified_at.isoformat()
        return None

    def get_stats(self, obj):
        if hasattr(obj, 'resolver_profile'):
            return obj.resolver_profile.get_stats()
        return {}


class UserSettingsSerializer(serializers.Serializer):
    """Serializer for user settings."""
    notifications = serializers.DictField(required=False)
    privacy = serializers.DictField(required=False)
    preferences = serializers.DictField(required=False)
