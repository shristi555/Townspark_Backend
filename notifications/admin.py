from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'type', 'title', 'read', 'created_at']
    list_filter = ['type', 'read', 'created_at']
    search_fields = ['title', 'message', 'user__email', 'user__full_name']
    raw_id_fields = ['user', 'issue', 'actor']
    readonly_fields = ['id', 'created_at']
