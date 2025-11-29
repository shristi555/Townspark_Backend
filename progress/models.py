from django.db import models
from django.conf import settings


def progress_image_path(instance, filename):
    """Generate upload path for progress images."""
    ext = filename.split(".")[-1]
    return f"progress_images/issue_{instance.progress.issue.id}/progress_{instance.progress.id}_{instance.id}.{ext}"


class Progress(models.Model):
    """
    Model representing a progress update for an issue.
    
    Progress updates track the status changes and work done on issues.
    Only staff members can create progress updates.
    """

    STATUS_CHOICES = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
    ]

    issue = models.ForeignKey(
        "issue.Issue",
        on_delete=models.CASCADE,
        related_name="progress_updates",
        help_text="The issue this progress update is related to"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        help_text="The current status of the issue after this update"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Optional notes about this progress update"
    )
    
    # Timestamps
    updated_at = models.DateTimeField(auto_now_add=True)
    
    # Relationships
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="progress_updates",
        help_text="The staff member who made this progress update"
    )

    class Meta:
        db_table = "progress"
        verbose_name = "Progress Update"
        verbose_name_plural = "Progress Updates"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Progress for Issue #{self.issue.id} - {self.status}"

    def save(self, *args, **kwargs):
        """Save progress and update the related issue's status."""
        super().save(*args, **kwargs)
        # Update the issue's status to match this progress update
        if self.issue.status != self.status:
            self.issue.status = self.status
            if self.status == "resolved":
                self.issue.resolved_by = self.updated_by
            self.issue.save()


class ProgressImage(models.Model):
    """
    Model for storing multiple images associated with a progress update.
    """

    progress = models.ForeignKey(
        Progress,
        on_delete=models.CASCADE,
        related_name="images",
        help_text="The progress update this image belongs to"
    )
    image = models.ImageField(
        upload_to=progress_image_path,
        help_text="Image related to the progress update"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "progress_images"
        verbose_name = "Progress Image"
        verbose_name_plural = "Progress Images"
        ordering = ["uploaded_at"]

    def __str__(self):
        return f"Image for Progress #{self.progress.id}"
