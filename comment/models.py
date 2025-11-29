from django.db import models
from django.conf import settings


class Comment(models.Model):
    """
    Model representing a comment on an issue.
    
    Users can comment on issues to provide additional information,
    ask questions, or discuss the issue.
    """
    
    issue = models.ForeignKey(
        "issue.Issue",
        on_delete=models.CASCADE,
        related_name="comments",
        help_text="The issue this comment is related to"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
        help_text="The user who made this comment"
    )
    content = models.TextField(
        help_text="The content of the comment"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the comment was created"
    )

    class Meta:
        db_table = "comments"
        ordering = ["-created_at"]
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        return f"Comment by {self.user.email} on Issue #{self.issue.id}"
