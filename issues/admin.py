from django.contrib import admin
from .models import (
    Issue, IssueImage, IssueTimeline, OfficialResponse, 
    Comment, CommentLike, Upvote, Bookmark
)


class IssueImageInline(admin.TabularInline):
    model = IssueImage
    extra = 0


class IssueTimelineInline(admin.TabularInline):
    model = IssueTimeline
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'category', 'status', 'urgency', 'reporter', 'created_at']
    list_filter = ['status', 'urgency', 'category', 'is_anonymous', 'created_at']
    search_fields = ['id', 'title', 'description', 'address', 'area']
    readonly_fields = ['id', 'created_at', 'updated_at', 'upvote_count', 'comment_count']
    inlines = [IssueImageInline, IssueTimelineInline]
    raw_id_fields = ['reporter', 'assigned_resolver']


@admin.register(IssueImage)
class IssueImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'issue', 'is_after_image', 'uploaded_at']
    list_filter = ['is_after_image', 'uploaded_at']


@admin.register(IssueTimeline)
class IssueTimelineAdmin(admin.ModelAdmin):
    list_display = ['issue', 'status', 'updated_by', 'created_at']
    list_filter = ['status', 'created_at']


@admin.register(OfficialResponse)
class OfficialResponseAdmin(admin.ModelAdmin):
    list_display = ['issue', 'department', 'responder', 'created_at']
    list_filter = ['department', 'created_at']
    raw_id_fields = ['issue', 'responder']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'issue', 'author', 'like_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content']
    raw_id_fields = ['issue', 'author', 'parent']


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'comment', 'created_at']


@admin.register(Upvote)
class UpvoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'issue', 'created_at']
    raw_id_fields = ['user', 'issue']


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'issue', 'created_at']
    raw_id_fields = ['user', 'issue']
