from django.contrib import admin
from .models import Issue


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    """Admin configuration for the Issue model."""

    list_display = (
        "id",
        "title",
        "status",
        "created_by",
        "resolved_by",
        "created_at",
        "updated_at",
    )
    list_filter = ("status", "created_at", "updated_at")
    search_fields = ("title", "description", "created_by__email")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("title", "description")}),
        ("Status", {"fields": ("status", "resolved_by")}),
        ("Creator", {"fields": ("created_by",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related("created_by", "resolved_by")
