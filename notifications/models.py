import uuid
from django.db import models
from django.conf import settings


class Notification(models.Model):
    """
    Notification model for user notifications.
    """
    class NotificationType(models.TextChoices):
        STATUS_UPDATE = 'status_update', 'Status Update'
        COMMENT = 'comment', 'New Comment'
        UPVOTE = 'upvote', 'Upvote'
        MENTION = 'mention', 'Mention'
        RESOLUTION = 'resolution', 'Resolution'
        ASSIGNMENT = 'assignment', 'Assignment'
        SYSTEM = 'system', 'System'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    type = models.CharField(
        max_length=20,
        choices=NotificationType.choices
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    issue = models.ForeignKey(
        'issues.Issue',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='triggered_notifications'
    )
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user}: {self.title}"

    @classmethod
    def create_status_update_notification(cls, issue, actor=None):
        """Create a notification for status update."""
        status_names = {
            'reported': 'reported',
            'acknowledged': 'acknowledged',
            'in-progress': 'is now in progress',
            'resolved': 'has been resolved'
        }
        
        return cls.objects.create(
            user=issue.reporter,
            type=cls.NotificationType.STATUS_UPDATE,
            title="Status Update",
            message=f"Your issue '{issue.title}' {status_names.get(issue.status, 'has been updated')}.",
            issue=issue,
            actor=actor
        )

    @classmethod
    def create_comment_notification(cls, comment):
        """Create a notification for new comment."""
        # Don't notify if user comments on their own issue
        if comment.author == comment.issue.reporter:
            return None
        
        return cls.objects.create(
            user=comment.issue.reporter,
            type=cls.NotificationType.COMMENT,
            title="New Comment",
            message=f"{comment.author.full_name} commented on your issue '{comment.issue.title}'.",
            issue=comment.issue,
            actor=comment.author
        )

    @classmethod
    def create_upvote_notification(cls, upvote):
        """Create a notification for upvote."""
        # Don't notify if user upvotes their own issue
        if upvote.user == upvote.issue.reporter:
            return None
        
        return cls.objects.create(
            user=upvote.issue.reporter,
            type=cls.NotificationType.UPVOTE,
            title="New Upvote",
            message=f"Someone upvoted your issue '{upvote.issue.title}'.",
            issue=upvote.issue,
            actor=upvote.user
        )

    @classmethod
    def create_assignment_notification(cls, issue, resolver):
        """Create a notification for issue assignment."""
        return cls.objects.create(
            user=resolver,
            type=cls.NotificationType.ASSIGNMENT,
            title="New Assignment",
            message=f"You have been assigned to issue '{issue.title}'.",
            issue=issue,
            actor=None
        )

    @classmethod
    def create_resolution_notification(cls, issue, actor=None):
        """Create a notification for issue resolution."""
        return cls.objects.create(
            user=issue.reporter,
            type=cls.NotificationType.RESOLUTION,
            title="Issue Resolved",
            message=f"Great news! Your issue '{issue.title}' has been resolved.",
            issue=issue,
            actor=actor
        )
