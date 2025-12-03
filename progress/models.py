from django.db import models
from django.conf import settings


def progress_image_path(instance, filename):
    """Generate upload path for progress images."""
    ext = filename.split(".")[-1]
    return f"progress_images/issue_{instance.progress.issue.id}/progress_{instance.progress.id}_{instance.id}.{ext}"


class Progress(models.Model):
    """
    Model representing a progress update for an issue.
    
    Progress updates track the work done on issues.
    Only the reporter, admin, or staff members can create progress updates.
    Each progress entry is linked to an issue and contains a description
    and optional images.
    """

    issue = models.ForeignKey(
        "issue.Issue",
        on_delete=models.CASCADE,
        related_name="progress_updates",
        help_text="The issue this progress update is related to"
    )
    description = models.TextField(
        help_text="A detailed description of the progress update"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Relationships
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="progress_updates",
        help_text="The user who made this progress update"
    )

    class Meta:
        db_table = "progress"
        verbose_name = "Progress Update"
        verbose_name_plural = "Progress Updates"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Progress for Issue #{self.issue.id} by {self.updated_by}"

    def save(self, *args, **kwargs):
        """Save progress and update the related issue's updated_at timestamp."""
        super().save(*args, **kwargs)
        # Update the issue's updated_at timestamp when new progress is added
        self.issue.save(update_fields=["updated_at"])


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
        upload_to="progress_images/",
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
