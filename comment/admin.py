from django.contrib import admin
from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin configuration for Comment model."""
    
    list_display = ["id", "issue", "user", "content_preview", "created_at"]
    list_filter = ["created_at", "issue"]
    search_fields = ["content", "user__email", "issue__title"]
    readonly_fields = ["created_at"]
    ordering = ["-created_at"]
    
    def content_preview(self, obj):
        """Return a truncated preview of the comment content."""
        if len(obj.content) > 50:
            return f"{obj.content[:50]}..."
        return obj.content
    content_preview.short_description = "Content"
