from django.contrib import admin
from .models import Progress, ProgressImage


class ProgressImageInline(admin.TabularInline):
    """Inline admin for ProgressImage to display images within the Progress admin."""
    model = ProgressImage
    extra = 0
    readonly_fields = ("uploaded_at",)


@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    """Admin configuration for Progress model."""
    list_display = ("id", "issue", "updated_by", "created_at")
    list_filter = ("created_at", "updated_by")
    search_fields = ("description", "issue__title")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
    inlines = [ProgressImageInline]
    
    fieldsets = (
        (None, {
            "fields": ("issue", "description")
        }),
        ("User Info", {
            "fields": ("updated_by",)
        }),
        ("Timestamps", {
            "fields": ("created_at",),
            "classes": ("collapse",)
        }),
    )


@admin.register(ProgressImage)
class ProgressImageAdmin(admin.ModelAdmin):
    """Admin configuration for ProgressImage model."""
    list_display = ("id", "progress", "image", "uploaded_at")
    list_filter = ("uploaded_at",)
    readonly_fields = ("uploaded_at",)
    ordering = ("-uploaded_at",)
