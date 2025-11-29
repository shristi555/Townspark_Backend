from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for the custom User model."""

    list_display = (
        "email",
        "full_name",
        "is_active",
        "is_staff",
        "is_admin",
        "date_joined",
    )
    list_filter = ("is_active", "is_staff", "is_admin", "date_joined")
    search_fields = ("email", "full_name", "phone_number")
    ordering = ("-date_joined",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal Info",
            {"fields": ("full_name", "phone_number", "address", "profile_image")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_admin",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "full_name",
                    "is_active",
                    "is_staff",
                    "is_admin",
                ),
            },
        ),
    )

    readonly_fields = ("date_joined", "last_login")
