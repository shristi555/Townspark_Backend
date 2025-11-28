import uuid
from django.db import models
from django.conf import settings


def issue_image_path(instance, filename):
    """Generate upload path for issue images."""
    ext = filename.split('.')[-1]
    return f"issue_images/{instance.issue.id}/{uuid.uuid4()}.{ext}"


def after_image_path(instance, filename):
    """Generate upload path for after (resolved) images."""
    ext = filename.split('.')[-1]
    return f"issue_images/{instance.issue.id}/after_{uuid.uuid4()}.{ext}"


class Issue(models.Model):
    """
    Main Issue model for civic issues reported by citizens.
    """
    class Status(models.TextChoices):
        REPORTED = 'reported', 'Reported'
        ACKNOWLEDGED = 'acknowledged', 'Acknowledged'
        IN_PROGRESS = 'in-progress', 'In Progress'
        RESOLVED = 'resolved', 'Resolved'

    class Urgency(models.TextChoices):
        LOW = 'low', 'Low'
        NORMAL = 'normal', 'Normal'
        HIGH = 'high', 'High'
        CRITICAL = 'critical', 'Critical'

    id = models.CharField(max_length=20, primary_key=True)  # Format: TS-XXXX
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(
        'core.Category', 
        on_delete=models.PROTECT,
        related_name='issues'
    )
    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.REPORTED
    )
    urgency = models.CharField(
        max_length=20, 
        choices=Urgency.choices, 
        default=Urgency.NORMAL
    )

    # Location
    address = models.TextField()
    area = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Relations
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='issues'
    )
    assigned_resolver = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_issues'
    )
    department = models.ForeignKey(
        'core.Department', 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        related_name='issues'
    )

    # Flags
    is_anonymous = models.BooleanField(default=False)

    # Counters (denormalized for performance)
    upvote_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    share_count = models.PositiveIntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.id}: {self.title}"

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = self.generate_issue_id()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_issue_id():
        """Generate a unique issue ID in format TS-XXXX."""
        last_issue = Issue.objects.order_by('-created_at').first()
        if last_issue:
            try:
                num = int(last_issue.id.split('-')[1]) + 1
            except (IndexError, ValueError):
                num = 1000
        else:
            num = 1000
        return f"TS-{num}"

    def update_comment_count(self):
        """Update the comment count from the database."""
        self.comment_count = self.comments.count()
        self.save(update_fields=['comment_count'])

    def update_upvote_count(self):
        """Update the upvote count from the database."""
        self.upvote_count = self.upvotes.count()
        self.save(update_fields=['upvote_count'])


class IssueImage(models.Model):
    """
    Model for storing issue images.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    issue = models.ForeignKey(
        Issue, 
        on_delete=models.CASCADE, 
        related_name='images'
    )
    image = models.ImageField(upload_to=issue_image_path)
    is_after_image = models.BooleanField(default=False)  # For resolved issue comparison
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['uploaded_at']

    def __str__(self):
        return f"Image for {self.issue.id}"


class IssueTimeline(models.Model):
    """
    Model for tracking issue status changes.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    issue = models.ForeignKey(
        Issue, 
        on_delete=models.CASCADE, 
        related_name='timeline'
    )
    status = models.CharField(max_length=20, choices=Issue.Status.choices)
    note = models.TextField(blank=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.issue.id} - {self.status}"


class OfficialResponse(models.Model):
    """
    Official response from a department/resolver for an issue.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    issue = models.OneToOneField(
        Issue, 
        on_delete=models.CASCADE, 
        related_name='official_response'
    )
    department = models.ForeignKey(
        'core.Department', 
        on_delete=models.SET_NULL, 
        null=True
    )
    message = models.TextField()
    responder = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Official Response for {self.issue.id}"


class Comment(models.Model):
    """
    Comment model for issue discussions.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    issue = models.ForeignKey(
        Issue, 
        on_delete=models.CASCADE, 
        related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField()
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='replies'
    )
    like_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author} on {self.issue.id}"

    def update_like_count(self):
        """Update the like count from the database."""
        self.like_count = self.likes.count()
        self.save(update_fields=['like_count'])


class CommentLike(models.Model):
    """
    Model for tracking comment likes.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='comment_likes'
    )
    comment = models.ForeignKey(
        Comment, 
        on_delete=models.CASCADE, 
        related_name='likes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'comment']

    def __str__(self):
        return f"{self.user} likes comment {self.comment.id}"


class Upvote(models.Model):
    """
    Model for tracking issue upvotes.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='upvotes'
    )
    issue = models.ForeignKey(
        Issue, 
        on_delete=models.CASCADE, 
        related_name='upvotes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'issue']

    def __str__(self):
        return f"{self.user} upvoted {self.issue.id}"


class Bookmark(models.Model):
    """
    Model for tracking bookmarked issues.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='bookmarks'
    )
    issue = models.ForeignKey(
        Issue, 
        on_delete=models.CASCADE, 
        related_name='bookmarks'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'issue']

    def __str__(self):
        return f"{self.user} bookmarked {self.issue.id}"
