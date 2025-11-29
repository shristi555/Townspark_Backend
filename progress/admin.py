from django.contrib import admin
from .models import Progress, ProgressImage


class ProgressImageInline(admin.TabularInline):
    """Inline admin for progress images."""
    model = ProgressImage
    extra = 1
    readonly_fields = ("uploaded_at",)


@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    """Admin configuration for the Progress model."""

    list_display = (
        "id",
        "issue",
        "status",
        "updated_by",
        "updated_at",
        "image_count",
    )
    list_filter = ("status", "updated_at")
    search_fields = ("issue__title", "notes", "updated_by__email")
    ordering = ("-updated_at",)
    readonly_fields = ("updated_at",)
    inlines = [ProgressImageInline]

    fieldsets = (
        (None, {"fields": ("issue", "status", "notes")}),
        ("Updated By", {"fields": ("updated_by",)}),
        ("Timestamps", {"fields": ("updated_at",)}),
    )

    def get_queryset(self, request):
        """Optimize queryset with select_related and prefetch_related."""
        return super().get_queryset(request).select_related(
            "issue", "updated_by"
        ).prefetch_related("images")

    def image_count(self, obj):
        """Return the number of images for this progress update."""
        return obj.images.count()
    image_count.short_description = "Images"


@admin.register(ProgressImage)
class ProgressImageAdmin(admin.ModelAdmin):
    """Admin configuration for the ProgressImage model."""

    list_display = ("id", "progress", "image", "uploaded_at")
    list_filter = ("uploaded_at",)
    search_fields = ("progress__issue__title",)
    ordering = ("-uploaded_at",)
    readonly_fields = ("uploaded_at",)
