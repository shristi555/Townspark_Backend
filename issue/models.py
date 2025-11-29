from django.db import models
from django.conf import settings


class Issue(models.Model):
    """
    Model representing an issue/complaint created by users.
    
    Issues can have four statuses:
    - open: Newly created issue
    - in_progress: Issue is being worked on
    - resolved: Issue has been resolved
    - closed: Issue has been closed
    """

    STATUS_CHOICES = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default="open"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Relationships
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_issues",
        help_text="The user who created this issue"
    )
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_issues",
        help_text="The staff member who resolved this issue"
    )

    class Meta:
        db_table = "issues"
        verbose_name = "Issue"
        verbose_name_plural = "Issues"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.status})"

    def mark_in_progress(self, user):
        """Mark issue as in progress."""
        self.status = "in_progress"
        self.save()

    def resolve(self, user):
        """Mark issue as resolved by a staff member."""
        self.status = "resolved"
        self.resolved_by = user
        self.save()

    def close(self):
        """Mark issue as closed."""
        self.status = "closed"
        self.save()

    def reopen(self):
        """Reopen a closed or resolved issue."""
        self.status = "open"
        self.resolved_by = None
        self.save()
