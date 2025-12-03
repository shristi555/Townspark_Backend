from django.contrib import admin
from .models import Category, Issue, IssueImage


class IssueImageInline(admin.TabularInline):
    """Inline admin for IssueImage to display images within the Issue admin."""
    model = IssueImage
    extra = 0
    readonly_fields = ("uploaded_at",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for Category model."""
    list_display = ("id", "name", "description")
    search_fields = ("name", "description")
    ordering = ("name",)


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    """Admin configuration for Issue model."""
    list_display = ("id", "title", "status", "category", "reported_by", "created_at", "updated_at")
    list_filter = ("status", "category", "created_at")
    search_fields = ("title", "description", "location")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
    inlines = [IssueImageInline]
    
    fieldsets = (
        (None, {
            "fields": ("title", "description", "location")
        }),
        ("Classification", {
            "fields": ("category", "status")
        }),
        ("Reporter", {
            "fields": ("reported_by",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )


@admin.register(IssueImage)
class IssueImageAdmin(admin.ModelAdmin):
    """Admin configuration for IssueImage model."""
    list_display = ("id", "issue", "image", "uploaded_at")
    list_filter = ("uploaded_at",)
    readonly_fields = ("uploaded_at",)
    ordering = ("-uploaded_at",)
