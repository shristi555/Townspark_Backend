from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ResolverProfile, UserBadge


class ResolverProfileInline(admin.StackedInline):
    model = ResolverProfile
    fk_name = 'user'  # Specify the foreign key to use
    can_delete = False
    verbose_name_plural = 'Resolver Profile'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'full_name', 'role', 'is_active', 'is_staff', 'created_at']
    list_filter = ['role', 'is_active', 'is_staff', 'created_at']
    search_fields = ['email', 'full_name']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'phone_number', 'address', 'ward', 'bio', 'location', 'profile_image')}),
        ('Role', {'fields': ('role',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'password1', 'password2', 'role'),
        }),
    )
    
    inlines = [ResolverProfileInline]

    def get_inlines(self, request, obj=None):
        if obj and obj.role == 'resolver':
            return [ResolverProfileInline]
        return []


@admin.register(ResolverProfile)
class ResolverProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'department', 'designation', 'employee_id', 'is_verified']
    list_filter = ['is_verified', 'department']
    search_fields = ['user__email', 'user__full_name', 'employee_id']
    raw_id_fields = ['user', 'verified_by']


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ['user', 'badge', 'earned_at']
    list_filter = ['badge', 'earned_at']
    raw_id_fields = ['user']